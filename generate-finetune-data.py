import json
import argparse
import openai
import time
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_explanation_for_sql(input_sequence, output_sequence):
    prompt = f"Provide a simple explanation for the SQL query generated based on the given input:\n\nInput: {input_sequence}\n\nSQL: {output_sequence}"

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a capable SQL teacher. Add an easy-to-understand short explanation for this text-to-SQL conversion. You are trying to create a chain of thought from the natural language to the SQL query. The SQL with the _ is just the skeleton code, you dont need to explain that part. Keep it short."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256,
            )

            explanation = response.choices[0]['message']['content'].replace("Explanation:", "").strip()
            return explanation
        
        except Exception as e:
            print(f'Error occurred while fetching explanation: {str(e)}')
            print('Waiting for 10 seconds before retrying...')
            time.sleep(10)

def process_dataset(input_dataset_path, output_dataset_path, mode, sql_type, use_skeleton, explanation):
    # Load the input dataset
    dataset = json.load(open(input_dataset_path, "r"))
    output_dataset = []

    for data in tqdm(dataset, desc="Processing dataset"):
        db_id = data["db_id"]
        tc_original = []
        input_sequence = data["question"] + " | "
        for table in data["db_schema"]:
            input_sequence += table["table_name_original"] + " : "
            input_sequence += " , ".join(table["column_names_original"]) + " | "
            for column_name_original in table["column_names_original"]:
                tc_original.append(table["table_name_original"]+"."+column_name_original)

        for fk in data["fk"]:
            input_sequence += fk["source_table_name_original"]+"."+fk["source_column_name_original"]+" = "+fk["target_table_name_original"]+"."+fk["target_column_name_original"] + " | "
        
        if sql_type == "natsql":
            output_sequence = data["natsql_skeleton"] + " | " + data["natsql"] if use_skeleton else data["natsql"]
        else: # regular sql
            output_sequence = data["sql_skeleton"] + " | " + data["norm_sql"] if use_skeleton else data["norm_sql"]

        if mode == "train":
            if explanation:
                sql_explanation = get_explanation_for_sql(input_sequence, output_sequence)
                text = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n\nConvert text to {sql_type}: " + input_sequence + "\n\n" + f"### Explanation:\n\n{sql_explanation}\n\n" + "### Response:\n\n" + output_sequence
            else:
                text = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n\nConvert text to {sql_type}: " + input_sequence + "\n\n" + "### Response:\n\n" + output_sequence
            output_dataset.append({
                "db_id": db_id,
                "text": text,
            })
        else: # validation mode
            prompt = input_sequence
            ground_truth = output_sequence
            output_dataset.append({
                "db_id": db_id,
                "prompt": prompt,
                "ground_truth": ground_truth,
            })

        # Save the output dataset after every iteration
        with open(output_dataset_path, "w") as f:
            json.dump(output_dataset, f, indent=2, ensure_ascii=False)


def main(mode, sql_type, use_skeleton, explanation):
    if mode == "train":
        process_dataset("./data/preprocessed/preprocessed_train_spider_natsql.json", f"./data/train_{sql_type}{'_skeleton' if use_skeleton else ''}.json", mode, sql_type, use_skeleton, explanation)
    elif mode == "validation":
        process_dataset("./data/preprocessed/preprocessed_dev_natsql.json", f"./data/validation_{sql_type}{'_skeleton' if use_skeleton else ''}.json", mode, sql_type, use_skeleton, explanation)
    elif mode == "both":
        process_dataset("./data/preprocessed/preprocessed_train_spider_natsql.json", f"./data/train_{sql_type}{'_skeleton' if use_skeleton else ''}.json", "train", sql_type, use_skeleton, explanation)
        process_dataset("./data/preprocessed/preprocessed_dev_natsql.json", f"./data/validation_{sql_type}{'_skeleton' if use_skeleton else ''}.json", "validation", sql_type, use_skeleton, explanation)
    else:
        print("Specify mode flag with `--mode [train / validation / both].")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default="both", help="Specify mode flag with `--mode [train / validation / both].")
    parser.add_argument('--sql_type', type=str, required=True, help="Specify SQL type with `--sql_type [natsql / sql].")
    parser.add_argument('--skeleton', action='store_true', default=False, help="Use SQL skeleton in the output sequence.")
    parser.add_argument('--explanation', action='store_true', default=False, help="Fetch explanation for SQL from ChatGPT.")
    args = parser.parse_args()

    main(args.mode, args.sql_type, args.skeleton, args.explanation)
