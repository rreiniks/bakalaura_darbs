import matplotlib.pyplot as plt
import json
import os

import numpy as np


#subcategory = input("Please specify a computing subcategory (SE, CE, CS, DS, IS, IT, CB): ").strip()

paths = {
    "SE": "Software engineering",
    "CE": "Computer engineering",
    "CS": "Computer science",
    #"DS": "Data science",
    "IS": "Information systems",
    "IT": "Information technology",
    #"CB": "Cybersecurity"
}

#if subcategory not in paths:
    #raise ValueError("Invalid subcategory specified.")

course_top1_similarities = {}

for subcategory in paths:
    file_path = f'Guidelines/{paths[subcategory]}/results/similar_areas.json'
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
    
    with open(file_path, 'r') as file:
        data = json.load(file)

    for course in data:
        if course['similarities']:
            course_code = course['code']
            course_kp = course['kp']
            top1_similarity = course['similarities'][0][2]
            
            if course_code not in course_top1_similarities:
                course_top1_similarities[course_code] = []
            
            course_top1_similarities[course_code].append(top1_similarity)

average_top1_values = {course: np.mean(similarities) for course, similarities in course_top1_similarities.items()}

for subcategory in paths:

    with open(f'Guidelines/{paths[subcategory]}/results/similar_areas.json', 'r') as file:
        data = json.load(file)

    course_types = {"VSK": "darkblue", "NTP": "darkgreen", f"{subcategory}-o": "darkred"}

    course_names = []
    top1_areas = []
    top1_similarities = []
    colors = []

    for course in data:
        if course['similarities']:  
            course_name = course['code']
            course_type = course['type']
            course_kp = course['kp']
            
            
            top1_similarity = course['similarities'][0][2]
            top1_area_name = course['similarities'][0][1]  
            top1_area_code = course['similarities'][0][0]

            color = course_types.get(course_type, "darkred")
            
            #if top1_area_name.split(" - ")[-1]:
            
            course_names.append(course_name)
            top1_similarities.append(top1_similarity)
            top1_areas.append(top1_area_code)
            colors.append(color)

    sorted_data = sorted(zip(top1_similarities, course_names, top1_areas, colors), reverse=True)
    sorted_similarities, sorted_courses, sorted_areas, sorted_colors = zip(*sorted_data)

    plt.figure(figsize=(20, 10))
    bars = plt.bar(sorted_courses, sorted_similarities, color=sorted_colors)

    avg_values = [average_top1_values[course] for course in sorted_courses]
    plt.plot(sorted_courses, avg_values, 'o-', color='orange', alpha=0.5, label='Average Top1 Similarity')

    for bar, area in zip(bars, sorted_areas):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f' {area}', ha='center', va='bottom')

    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in course_types.values()]
    labels = course_types.keys()
    plt.legend(handles, labels, title="Course Types")

    plt.title('Top 1 Knowledge Area Similarity Scores for Each Course')
    plt.xlabel('Course Name')
    plt.ylabel('Similarity Score')
    plt.xticks(rotation=90)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    output_file = f'Guidelines/{paths[subcategory]}/results/top1_knowledge_area_similarity_scores.png'
    plt.savefig(output_file)
    plt.close()