import json
import random
from sqlparse import format
import sqlite3
import os
from scripts.helpers import generate_md_table, get_result_table_from_db

def create_markdown(json_data):
    markdown_content = ""
    counter = 1
    for item in json_data:
        question = item['question']
        difficulty = item['difficulty']
        sql_chatgpt = format(item['pred'], reindent=True, keyword_case='upper')
        gold = format(item['gold'], reindent=True, keyword_case='upper')
        db_info = item['db_info']
        db_id = item['db_id']

        # Get database path
        db_folder = os.path.join('./data/database/', item["db_id"])
        db_path = os.path.join(db_folder, f"{item['db_id']}.sqlite")

        # Get result table
        pred_cols, pred_results = get_result_table_from_db(db_path, sql_chatgpt)
        gold_cols, gold_results = get_result_table_from_db(db_path, gold)

        # Generate markdown table
        pred_table = generate_md_table(pred_cols, pred_results)
        gold_table = generate_md_table(gold_cols, gold_results)

        markdown_content += f"### {counter}. entry-{item['index']}\n"
        markdown_content += f"**Question:** {question}\n\n"
        markdown_content += f"**Difficulty:** {difficulty}\n\n"
        markdown_content += f"**DB Info:** {db_id}\n"
        markdown_content += f"```\n{db_info}```\n"
        markdown_content += "**SQLChatGPT:**\n"
        markdown_content += f"```sql\n{sql_chatgpt}\n```\n"
        markdown_content += f"{pred_table}\n\n"

        markdown_content += "**GOLD:**\n"
        markdown_content += f"```sql\n{gold}\n```\n\n"
        markdown_content += f"{gold_table}\n\n"

        counter += 1
    
    return markdown_content

# Load JSON data
with open('analysis/incorrect.json') as f:
    json_data = f.read()
data = json.loads(json_data)

# Filter data based on difficulty
extra_difficulty_queries = [item for item in data if item['difficulty'] == 'extra']
hard_difficulty_queries = [item for item in data if item['difficulty'] == 'hard']
medium_difficulty_queries = [item for item in data if item['difficulty'] == 'medium']

# Randomly select the required number of queries
selected_extra_difficulty_queries = random.sample(extra_difficulty_queries, min(15, len(extra_difficulty_queries)))
selected_hard_difficulty_queries = random.sample(hard_difficulty_queries, min(5, len(hard_difficulty_queries)))
selected_medium_difficulty_queries = random.sample(medium_difficulty_queries, min(5, len(medium_difficulty_queries)))

# Combine selected queries
selected_queries = selected_extra_difficulty_queries + selected_hard_difficulty_queries + selected_medium_difficulty_queries

# Generate Markdown content
markdown_content = create_markdown(selected_queries)

# Writing to a markdown file
with open("analysis/incorrect_random_sample.md", "w") as file:
    file.write(markdown_content)

print("Markdown file created successfully.")