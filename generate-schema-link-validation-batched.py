from concurrent.futures import ThreadPoolExecutor
import threading
import openai
import time
import json
from datasets import load_dataset
from tqdm import tqdm
import os
from dotenv import load_dotenv
import re

# output path
output_path = 'data/validation_sql_skeleton_gpt4.json'

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

context_dataset = load_dataset("richardr1126/spider-context-validation", split="validation")
spider_dataset = load_dataset("spider", split="validation")
last_line_written = 0

def extract_db_info(response):
    pattern = r'(?<=\|)[^|]+?(?=\|)'
    matches = re.findall(pattern, response)
    db_info_string = ' | '.join([match.strip() for match in matches]).strip()
    return '| ' + db_info_string + ' |'

# Global lock for writing to file
lock = threading.Lock()

def process_entry(i):
    context_dataset_entry = context_dataset[i]
    spider_dataset_entry = spider_dataset[i]

    prompt = context_dataset_entry["prompt"]
    pre_prompt = """
        Given the question and database information, perform the following actions:
        1 - Rank the columns in each table based on the possibility of being used in the SQL, Column that matches more with the question words or the foreign key is highly relevant and must be placed ahead. You should output them in the order of the most relevant to the least relevant. Explain why you choose each column.
        2 - Output a database info string that contains all the columns and keys in each table according to your explanation. The db info string should be all on one line (including the foreign/primary keys) in the following format: | table01: col01, col02, ... | table02: col01, ... | ... \n\n
    """
    spider_question = spider_dataset_entry["question"]
    db_id = context_dataset_entry["db_id"]
    ground_truth = context_dataset_entry["ground_truth"]

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": pre_prompt+prompt}
                ],
                #temperature=0.7,
            )
            response_text = response['choices'][0]['message']['content']
            db_info = extract_db_info(response_text)
            db_info = db_info.replace('|  |', '|')

            output_entry = {
                "index": i,  # For debugging purposes
                "db_id": db_id,
                "question": spider_question,
                "db_info": db_info,
                "ground_truth": ground_truth
            }

            # Append the output_entry to the existing list
            with lock:
                output_dataset[i] = output_entry

            # Write the updated list back to the JSON file
            with lock:
                with open(output_path, 'w') as f:
                    json.dump(output_dataset, f, indent=2, ensure_ascii=False)

            break
            
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            print('Waiting for 10 seconds before retrying...')
            time.sleep(10)


# Initialize the list by reading from the existing JSON file or create a new list if the file doesn't exist.
try:
    with open(output_path, 'r') as f:
        output_dataset = json.load(f)
except FileNotFoundError:
    output_dataset = [None] * len(context_dataset)  # Pre-allocate list with Nones

with ThreadPoolExecutor(max_workers=8) as executor:  # You can change max_workers based on your system capabilities
    list(tqdm(executor.map(process_entry, range(last_line_written, len(context_dataset))), total=len(context_dataset)-last_line_written))
