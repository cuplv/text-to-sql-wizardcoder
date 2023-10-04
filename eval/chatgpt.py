import openai
import time
from datasets import load_dataset
from tqdm import tqdm
import os
from dotenv import load_dotenv
from scripts.schema_helpers import ask_chatgpt
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

last_line_written = 0

# Define the function that fetches the response for a given entry.
def fetch_response(i, entry):
    prompt = f"""
    ### Complete sqlite SQL query only and with no explanation
    ### Sqlite SQL tables, with their properties:
    #
    {entry['db_info']}
    #
    ### {entry['question']}
    SELECT
    """
    
    response_text = "SELECT " + ask_chatgpt(prompt).strip().replace("\n", " ").replace("\t", " ")
    
    if response_text[-1] == ".":
        response_text = response_text[:-1]

    return i, response_text

with open('../data/validation_sql_ranked.json', 'r') as f:
    dataset = json.load(f)

responses = {}
# Using ThreadPoolExecutor to parallelize the work
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(fetch_response, i, entry) for i, entry in enumerate(dataset[last_line_written:])]
    for future in tqdm(as_completed(futures), total=len(dataset)-last_line_written, desc="Generating responses"):
        idx, response_text = future.result()
        responses[idx] = response_text

# Sort responses by index and then write to the file
sorted_responses = [responses[i] for i in sorted(responses.keys())]

with open('predictions/chatgpt_clear_context.txt', 'a') as f:
    for response_text in sorted_responses:
        f.write(response_text + "\n")
