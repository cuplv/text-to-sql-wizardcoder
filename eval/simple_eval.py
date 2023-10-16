import sqlite3
import json
import os
import argparse
from tqdm import tqdm

def execute_sql_on_db(db_path, sql_query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        #print(f"Error executing query: {sql_query} on database {db_path}. Error: {e}")
        return None


def evaluate(predictions_path, dataset_path, db_root_path):
    with open(predictions_path, 'r') as f:
        predictions = [line.strip() for line in f.readlines()]
    
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    correct_count = 0
    total_count = len(dataset)

    for idx, entry in tqdm(enumerate(dataset), total=total_count, desc="Evaluating"):
        db_path = os.path.join(db_root_path, entry["db_id"], entry["db_id"] + ".sqlite")
        ground_truth = entry['ground_truth']
        predicted_sql = predictions[idx]

        gt_results = execute_sql_on_db(db_path, ground_truth)
        pred_results = execute_sql_on_db(db_path, predicted_sql)

        if gt_results and pred_results:
            if set(gt_results) == set(pred_results):
                correct_count += 1

    accuracy = correct_count / total_count
    print(f"\nAccuracy: {accuracy:.4f} ({correct_count}/{total_count})")
    print("Evaluation completed.")  # This is to check if the function finishes successfully


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SQL Predictions")
    parser.add_argument("--predictions_path", type=str, default="predictions/chatgpt_error_few_shot.txt", help="Path to the predictions file.")
    parser.add_argument("--dataset_path", type=str, default="../data/validation_sql_ranked.json", help="Path to the dataset file.")
    parser.add_argument("--db_root_path", type=str, default="./data/database", help="Root path to the databases.")

    args = parser.parse_args()

    evaluate(args.predictions_path, args.dataset_path, args.db_root_path)
