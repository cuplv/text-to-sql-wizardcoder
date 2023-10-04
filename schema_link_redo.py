import time
import json
from datasets import load_dataset
from tqdm import tqdm

# import helpers
from eval.scripts.schema_helpers import reorder_tables, reorder_columns, extract_json_object, extract_list_object, ask_chatgpt

# output path
output_path = 'data/validation_sql_ranked.json'

context_dataset = load_dataset("richardr1126/spider-context-validation", split="validation")
last_line_written = 0

def process_entry(i):
    dataset_entry = context_dataset[i]

    prompt = f"""
    Given the database schema and question, perform the following actions:
    1 - Rank all the tables based on the possibility of being used in the SQL according to the question from
    the most relevant to the least relevant, Table or its column that matches more with the question words is
    highly relevant and must be placed ahead.
    2 - Check whether you consider all the tables.
    3 - Output a list object in the order of step 2, Your output should contain all the tables. The format should
    be like:
    [
    "table_1", "table_2", ...
    ]
    
    Schema:
    {dataset_entry['db_info']}
    
    Question:
    ### {dataset_entry['question']}
    """
    #print(prompt)
    response = ask_chatgpt(prompt)
    #print(response)
    ranked_tables = extract_list_object(response)
    #print(ranked_tables)
    reordered_schema = reorder_tables(dataset_entry['db_info'], ranked_tables)
    #print(reordered_schema)

    col_reorder_prompt = f"""
    Given the database tables and question, perform the following actions:
    1 - Rank the columns in each table based on the possibility of being used in the SQL, Column that
    matches more with the question words or the foreign key is highly relevant and must be placed ahead.
    You should output them in the order of the most relevant to the least relevant.
    Explain why you choose each column.
    2 - Output a JSON object that contains all the columns in each table according to your explanation. The
    format should be like:
    {{
    "table_1": ["column_1", "column_2", ......],
    "table_2": ["column_1", "column_2", ......],
    "table_3": ["column_1", "column_2", ......],
    ......
    }}

    Schema:
    {reordered_schema}

    Question:
    ### {dataset_entry['question']}
    """

    response = ask_chatgpt(col_reorder_prompt)
    #print(response)
    ranked_cols = extract_json_object(response)
    #print(ranked_cols)
    reordered_schema = reorder_columns(reordered_schema, ranked_cols)
    #print(reordered_schema)

    output_entry = {
        "index": i,  # For debugging purposes
        "db_id": dataset_entry["db_id"],
        "question": dataset_entry["question"],
        "db_info": reordered_schema, 
        "ground_truth": dataset_entry["ground_truth"],
    }

    # Append the output_entry to the existing list
    output_dataset[i] = output_entry

    # Write the updated list back to the JSON file
    with open(output_path, 'w') as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)

# Initialize the list by reading from the existing JSON file or create a new list if the file doesn't exist.
try:
    with open(output_path, 'r') as f:
        output_dataset = json.load(f)
except FileNotFoundError:
    output_dataset = [None] * len(context_dataset)  # Pre-allocate list with Nones

# Process entries in output_dataset where db_info is empty
for i, entry in enumerate(output_dataset):
    if entry is None or entry.get("db_info", "").strip() == "":
        print(f"Processing entry {i}...")
        process_entry(i)