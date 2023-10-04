import json
import argparse
import time
import os
from tqdm import tqdm

def process_dataset(input_dataset_path, output_dataset_path, mode, sql_type, use_skeleton, clear_context):
    # Load the input dataset
    dataset = json.load(open(input_dataset_path, "r"))
    output_dataset = []

    for data in tqdm(dataset, desc="Processing dataset"):
        db_id = data["db_id"]
        schema = ""
        if not clear_context:
            schema = " | "
            for table in data["db_schema"]:
                schema += table["table_name_original"] + " : "
                schema += " , ".join(table["column_names_original"]) + " | "
                
            for fk in data["fk"]:
                schema += fk["source_table_name_original"]+"."+fk["source_column_name_original"]+" = "+fk["target_table_name_original"]+"."+fk["target_column_name_original"] + " | "
            
            if sql_type == "natsql":
                output_sequence = data["natsql_skeleton"] + " | " + data["natsql"] if use_skeleton else data["natsql"]
            else: # regular sql
                output_sequence = data["sql_skeleton"] + " | " + data["norm_sql"] if use_skeleton else data["norm_sql"]
        else:
            for table in data["db_schema"]:
                schema += "# " + table["table_name_original"] + " ( "
                schema += " , ".join(table["column_names_original"]) + " )\n"

            for fk in data["fk"]:
                schema += "# " + fk["source_table_name_original"]+"."+fk["source_column_name_original"]+" = "+fk["target_table_name_original"]+"."+fk["target_column_name_original"] + "\n"
            
            if sql_type == "natsql":
                output_sequence = data["natsql_skeleton"] + " | " + data["natsql"] if use_skeleton else data["natsql"]
            else: # regular sql
                output_sequence = data["sql_skeleton"] + " | " + data["norm_sql"] if use_skeleton else data["norm_sql"]

        if mode == "train":
            text = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n\nConvert text to {sql_type}: " + data["question"] + schema + "\n\n" + "### Response:\n\n" + output_sequence
            output_dataset.append({
                "db_id": db_id,
                "text": text,
            })
        else: # validation mode
            ground_truth = output_sequence
            output_dataset.append({
                "db_id": db_id,
                "question": data["question"],
                "db_info": schema,
                "ground_truth": ground_truth,
            })

    with open(output_dataset_path, "w") as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)


def main(mode, sql_type, use_skeleton, clear_context):
    if mode == "train":
        process_dataset("./data/preprocessed/preprocessed_train_spider_natsql.json", f"./data/train_{sql_type}{'_skeleton' if use_skeleton else ''}.json", mode, sql_type, use_skeleton, clear_context)
    elif mode == "validation":
        process_dataset("./data/preprocessed/preprocessed_dev_natsql.json", f"./data/validation_{sql_type}{'_skeleton' if use_skeleton else ''}.json", mode, sql_type, use_skeleton, clear_context)
    elif mode == "both":
        process_dataset("./data/preprocessed/preprocessed_train_spider_natsql.json", f"./data/train_{sql_type}{'_skeleton' if use_skeleton else ''}.json", "train", sql_type, use_skeleton, clear_context)
        process_dataset("./data/preprocessed/preprocessed_dev_natsql.json", f"./data/validation_{sql_type}{'_skeleton' if use_skeleton else ''}.json", "validation", sql_type, use_skeleton, clear_context)
    else:
        print("Specify mode flag with `--mode [train / validation / both].")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default="both", help="Specify mode flag with `--mode [train / validation / both].")
    parser.add_argument('--sql_type', type=str, default='sql', help="Specify SQL type with `--sql_type [natsql / sql].", choices=['natsql', 'sql'])
    parser.add_argument('--skeleton', action='store_true', default=False, help="Use SQL skeleton in the output sequence.")
    parser.add_argument('--clear_context', action='store_true', default=False, help="Better schema layout for ChatGPT.")
    args = parser.parse_args()

    main(args.mode, args.sql_type, args.skeleton, args.clear_context)
