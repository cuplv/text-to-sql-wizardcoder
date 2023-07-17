import json

import json
import argparse

def process_dataset(input_dataset_path, output_dataset_path, mode):
    # Load the input dataset
    dataset = json.load(open(input_dataset_path, "r"))
    output_dataset = []

    for data in dataset:
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
        
        output_sequence = data["natsql"]

        # Generate text for training mode, prompt and ground_truth for validation mode
        if mode == "train":
            text = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n\nConvert text to NatSQL: " + input_sequence + "\n\n" + "### Response:\n\n" + output_sequence
            output_dataset.append({
                "db_id": db_id,
                "text": text,
                #"tc_original": tc_original
            })
        else: # validation mode
            prompt = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n\nConvert text to NatSQL: " + input_sequence + "\n\n### Response:\n\n"
            ground_truth = output_sequence
            output_dataset.append({
                "db_id": db_id,
                "prompt": prompt,
                "ground_truth": ground_truth,
                #"tc_original": tc_original
            })

    # Save the output dataset
    with open(output_dataset_path, "w") as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)

def main(mode):
    if mode == "train":
        process_dataset("./data/preprocessed/preprocessed_train_spider_natsql.json", "./data/train.json", "train")
    elif mode == "validation":
        process_dataset("./data/preprocessed/preprocessed_dev_natsql.json", "./data/validation.json", "validation")
    elif mode == "both":
        process_dataset("./data/preprocessed/preprocessed_train_spider_natsql.json", "./data/train.json", "train")
        process_dataset("./data/preprocessed/preprocessed_dev_natsql.json", "./data/validation.json", "validation")
    else:
        print("Specify mode flag with `--mode [train / validation / both].")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, required=True, help="Specify mode flag with `--mode [train / validation / both].")
    args = parser.parse_args()

    main(args.mode)

