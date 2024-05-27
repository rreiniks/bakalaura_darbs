from collections import Counter, defaultdict
import json
import math
import re
import nltk
from nltk.stem import WordNetLemmatizer
import string
import numpy as np


lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    words = nltk.word_tokenize(text)
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(lemmatized_words)


with open('stopwords.txt', 'r') as file:
    stopwords = set(file.read().splitlines())

def remove_stopwords(text, stopwords):

    translator = str.maketrans('', '', string.punctuation)
    
    text = text.translate(translator)
    
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stopwords]
    
    return ' '.join(filtered_words)


def get_term_frequencies(text):
    words = text.lower().split()
    term_count = Counter(words)
    total_terms = sum(term_count.values())
    term_frequencies = {term: count / total_terms for term, count in term_count.items()}
    return term_frequencies

def calculate_idf(documents):
    df = defaultdict(int)
    total_documents = len(documents)
    for document in documents:
        terms = set(document.split())
        for term in terms:
            df[term] += 1
    idf = {term: math.log(total_documents / df_count) for term, df_count in df.items()}
    return idf

def calculate_tf_idf(term_frequencies, idf_scores):
    tf_idf = {term: tf * idf_scores.get(term, 0) for term, tf in term_frequencies.items()}
    return tf_idf

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    return dot_product / (norm_vec1 * norm_vec2)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def compare_tf_idf(tf_idf_text, knowledge_units):
    similarities = []
    for unit in knowledge_units:
        for knowledge in unit["knowledge"]:
            unit_vector = []
            text_vector = []
            for term in tf_idf_text:
                unit_vector.append(knowledge["term_frequencies"].get(term, 0))
                text_vector.append(tf_idf_text[term])
            for term in knowledge["term_frequencies"]:
                if term not in tf_idf_text:
                    unit_vector.append(knowledge["term_frequencies"][term])
                    text_vector.append(0)
            similarity = cosine_similarity(np.array(text_vector), np.array(unit_vector))
            code = knowledge.get("code", "N/A")
            unit_name = knowledge.get("name", " ")
            #if similarity >= 0.05:
            similarities.append((unit["name"], code, unit_name, similarity))
    
    similarities.sort(key=lambda x: x[3], reverse=True)
    top_similar_units = similarities
    return top_similar_units

def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

def process_courses(file_path_a_general, file_path_a_field, file_path_b_core, knowledge_units):

    lines_a_general = read_file(file_path_a_general)
    lines_a_field = read_file(file_path_a_field)
    lines_b_core = read_file(file_path_b_core)
    lines = lines_a_general + lines_a_field + lines_b_core

    courses = []
    current_course = {"name": "", "content": [], "kp": 0, "type": "", "code": ""}

    course_code_pattern = re.compile(r'^[A-Za-z]{5}[0-9]{3}$')
    type = False

    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            if not current_course["name"]:
                current_course["name"] = stripped_line
            elif stripped_line.isdigit():
                current_course["kp"] = int(stripped_line)
                type = True
            elif type == True:
                type = False
                current_course["type"] = stripped_line
            elif course_code_pattern.match(stripped_line):
                current_course["code"] = stripped_line
                courses.append(current_course)
                current_course = {"name": "", "content": [], "kp": 0, "type": "", "code": ""}
            else:
                current_course["content"].append(stripped_line)

    results = []
    documents = []

    for course in courses:
        text = " ".join(course["content"])
        preprocessed_text = remove_stopwords(lemmatize_text(remove_stopwords(text, stopwords)), stopwords)
        documents.append(preprocessed_text)

    idf_scores = calculate_idf(documents)

    for course in courses:
        text = " ".join(course["content"])
        preprocessed_text = remove_stopwords(lemmatize_text(remove_stopwords(text, stopwords)), stopwords)
        term_frequencies = get_term_frequencies(preprocessed_text)
        tf_idf_text = calculate_tf_idf(term_frequencies, idf_scores)
        similar_units = compare_tf_idf(tf_idf_text, knowledge_units)
        results.append({
            "name": course["name"],
            "kp": course["kp"],
            "type": course["type"],
            "code": course["code"],
            "similarities": similar_units
        })

    return results

subcategory = input("Please specify a computing subcategory (SE, CE, CS, DS, IS, IT, CB): ").strip()

paths = {
    "SE": "Software engineering",
    "CE": "Computer engineering",
    "CS": "Computer science",
    "DS": "Data science",
    "IS": "Information systems",
    "IT": "Information technology",
    "CB": "Cybersecurity"
}

if subcategory not in paths:
    raise ValueError("Invalid subcategory specified.")

tf_idf_file_path = f'Guidelines/{paths[subcategory]}/tf_idf_unit.json'
a_core_field_file_path = 'A_courses_field.txt' #f'Guidelines/{paths[subcategory]}/courses.txt'
a_core_general_file_path = 'A_courses_general.txt'
b_core_curriculum_file_path = f'Guidelines/{paths[subcategory]}/B_core_courses.txt'
output_file_path = f'Guidelines/{paths[subcategory]}/results/similar_units.json'

knowledge_units = load_json(tf_idf_file_path)

results = process_courses(a_core_general_file_path, a_core_field_file_path, b_core_curriculum_file_path, knowledge_units)

with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(results, file, indent=4)