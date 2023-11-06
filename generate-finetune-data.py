import json
import argparse
import time
import os
from tqdm import tqdm

def process_dataset(input_dataset_path, output_dataset_path, mode, sql_type, use_skeleton, clear_context, ranked_schema, chatgpt_finetune):
    # Load the input dataset
    dataset = json.load(open(input_dataset_path, "r"))
    schema_dict = json.load(open(ranked_schema, "r"))
    output_dataset = []

    for i, data in enumerate(tqdm(dataset, desc="Processing dataset")):
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

        if mode != "validation" and not chatgpt_finetune:
            text = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n\nConvert text to {sql_type}: " + data["question"] + schema + "\n\n" + "### Response:\n\n" + output_sequence
            output_dataset.append({
                "db_id": db_id,
                "text": text,
            })
        elif chatgpt_finetune:
            prompt = f"""### Complete sqlite SQL query only and with no explanation, and do not select extra columns that are not explicitly requested in the query.
            ### Sqlite SQL tables, with their properties:
            #
            {schema if mode == "train" else schema_dict[i if i < 1034 else 0]['db_info']}
            #
            ### {data['question']}
            SELECT 
            """
            #remove white space from prompt
            prompt = prompt.replace("            ", "")
            #remove 'select' from output_sequence
            output_sequence = output_sequence[7:]
            output_dataset.append({
                "messages": [
                    {"role": "system", "content": "You are an excellent SQL writer."},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": output_sequence},
                ]
            })
        else: # validation mode
            ground_truth = output_sequence
            output_dataset.append({
                "db_id": db_id,
                "question": data["question"],
                "db_info": schema if mode == "train" else schema_dict[i if i < 1034 else 0]['db_info'],
                "ground_truth": ground_truth,
            })

    with open(output_dataset_path, "w") as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)
    
    with open(output_dataset_path+'l', "w", encoding='utf-8') as f:
        for entry in output_dataset:
            json_record = json.dumps(entry, ensure_ascii=False)
            f.write(json_record + "\n")


def main(mode, sql_type, use_skeleton, clear_context, chatgpt_finetune):
    ranked_schema = "./data/validation_sql_ranked.json"
    preprocessed_train = "./data/preprocessed/preprocessed_train_spider_natsql.json"
    preprocessed_dev = "./data/preprocessed/preprocessed_dev_natsql.json"
    skeleton_addon = "_skeleton" if use_skeleton else ""
    chatgpt_addon = "_chatgpt" if chatgpt_finetune else ""
    clear_addon = "_clear" if clear_context else ""

    train_fname = f"./data/train_{sql_type}{skeleton_addon}{chatgpt_addon}{clear_addon}.json"
    validation_fname = f"./data/validation_{sql_type}{skeleton_addon}{chatgpt_addon}{clear_addon}.json"

    if chatgpt_finetune:
        clear_context = True

    if mode == "train":
        process_dataset(preprocessed_train, train_fname, mode, sql_type, use_skeleton, clear_context, ranked_schema, chatgpt_finetune)
    elif mode == "validation":
        process_dataset(preprocessed_dev, validation_fname, mode, sql_type, use_skeleton, clear_context, ranked_schema, chatgpt_finetune)
    elif mode == "both":
        process_dataset(preprocessed_train, train_fname, "train", sql_type, use_skeleton, clear_context, ranked_schema, chatgpt_finetune)
        process_dataset(preprocessed_dev, validation_fname, "validation", sql_type, use_skeleton, clear_context, ranked_schema, chatgpt_finetune)
    else:
        print("Specify mode flag with `--mode [train / validation / both].")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default="both", help="Specify mode flag with `--mode [train / validation / both].")
    parser.add_argument('--sql_type', type=str, default='sql', help="Specify SQL type with `--sql_type [natsql / sql].", choices=['natsql', 'sql'])
    parser.add_argument('--skeleton', action='store_true', default=False, help="Use SQL skeleton in the output sequence.")
    parser.add_argument('--clear_context', action='store_true', default=False, help="Better schema layout for ChatGPT.")
    parser.add_argument('--chatgpt_finetune', action='store_true', default=False, help="Generate data for ChatGPT finetuning.")
    args = parser.parse_args()

    main(args.mode, args.sql_type, args.skeleton, args.clear_context, args.chatgpt_finetune)
