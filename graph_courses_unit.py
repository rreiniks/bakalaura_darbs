import matplotlib.pyplot as plt
import json
import os

paths = {
    "SE": "Software engineering",
    "CE": "Computer engineering",
    "CS": "Computer science",
    #"DS": "Data science",
    "IS": "Information systems",
    "IT": "Information technology",
    #"CB": "Cybersecurity"
}

for subcategory in paths:

    with open(f'Guidelines/{paths[subcategory]}/results/similar_units.json', 'r') as file:
        data = json.load(file)

    output_dir = f'Guidelines/{paths[subcategory]}/results/graphs/courses_units'
    os.makedirs(output_dir, exist_ok=True)

    course_types = {"VSK": "blue", "NTP": "green", f"{subcategory}-o": "red"}

    for course in data:
        course_name = course['name']
        course_type = course['type']
        color = course_types.get(course_type, "red")
        areas = []
        similarities = []
        
        for similarity in course['similarities']:
            areas.append(similarity[1])
            similarities.append(similarity[3])
        
        sorted_data = sorted(zip(similarities, areas), reverse=True)
        sorted_similarities, sorted_areas = zip(*sorted_data)
        
        plt.figure(figsize=(15, 10))
        plt.plot(sorted_areas, sorted_similarities, marker='o', linestyle='-', color=color, label='Similarity Scores')
        
        plt.title(f'Similarity Scores for "{course_name}" to Different Knowledge units')
        plt.xlabel('Knowledge unit')
        plt.ylabel('Similarity Score')
        plt.xticks(rotation=90)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        output_file = os.path.join(output_dir, f'{course_name}.png')
        plt.savefig(output_file)
        plt.close()