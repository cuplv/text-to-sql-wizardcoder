import sqlite3
import json
import os
import argparse
from tqdm import tqdm
import sqlparse
import glob
import re

def normalize_sql(sql):
    # Remove table names and aliases from columns
    sql = re.sub(r"\w+\.", "", sql)
    # Remove aliases altogether
    sql = re.sub(r" AS \w+", "", sql)
    # Normalize numbers and strings
    sql = re.sub(r"'\d+'", "'NUM'", sql)
    sql = re.sub(r"\d+", "NUM", sql)
    sql = re.sub(r"'[^']+'", "'STR'", sql)
    # Sort conditions for order-agnostic comparison
    conditions = re.findall(r"(WHERE|AND|OR) ([^AND|OR]+)", sql)
    conditions = sorted([cond[1] for cond in conditions])
    for cond in conditions:
        sql = sql.replace(cond, "", 1)
    sql = sql.replace("WHERE", "") + " WHERE " + " AND ".join(conditions)
    # Strip excessive spaces
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql

def format(text):
    # Split the text by "|", and get the last element in the list which should be the final query
    try:
        final_query = text.split("|")[1].strip()
    except Exception:
        final_query = text

    try:
        # Attempt to format SQL query using sqlparse
        formatted_query = sqlparse.format(final_query, reindent=True, keyword_case='upper')
    except Exception:
        # If formatting fails, use the original, unformatted query
        formatted_query = final_query

    # Convert SQL to markdown (not required, but just to show how to use the markdown module)
    final_query_markdown = f"{formatted_query}"

    return final_query_markdown

def execute_sql_on_db(db_path, sql_query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return None
    
def find_all_dbs_for_entry(db_folder):
    return glob.glob(os.path.join(db_folder, "*.sqlite"))

def evaluate(input, dataset_path, db_root_path, partial_match_threshold=0.8):
    with open(input, 'r') as f:
        input = [line.strip() for line in f.readlines()]
    
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    correct_count = 0
    partial_count = 0
    total_count = len(dataset)
    
    # Initialize the log for incorrect queries
    incorrect_queries = []

    for idx, entry in tqdm(enumerate(dataset), total=total_count, desc="Evaluating"):
        db_folder = os.path.join(db_root_path, entry["db_id"])
        all_dbs = find_all_dbs_for_entry(db_folder)

        ground_truth = format(entry['ground_truth'])
        predicted_sql = format(input[idx])

        gt_results = None
        pred_results = None
        for db_path in all_dbs:
            # Try executing the SQL on each database until we get non-empty results
            gt_results_temp = execute_sql_on_db(db_path, ground_truth)
            pred_results_temp = execute_sql_on_db(db_path, predicted_sql)
            
            if gt_results_temp and pred_results_temp:
                gt_results = gt_results_temp
                pred_results = pred_results_temp
                break

        if gt_results and pred_results:
            if set(gt_results) == set(pred_results):
                correct_count += 1
            else:
                # Calculate the similarity score
                common_rows = len(set(gt_results).intersection(set(pred_results)))
                similarity = common_rows / len(gt_results)

                # If similarity is above a certain threshold, consider it a partial match
                if similarity >= partial_match_threshold:
                    partial_count += 1
                else:
                    # Log the incorrect query
                    incorrect_queries.append({
                        'index': idx,
                        'db_id': entry['db_id'],
                        'db_info': entry['db_info'],
                        'question': entry['question'],
                        'predicted_sql': predicted_sql,
                        'ground_truth': ground_truth,
                        'similarity': similarity
                    })

    accuracy = (correct_count + partial_count * 0.5) / total_count
    print(f"\nAccuracy: {accuracy:.4f} ({correct_count + partial_count}/{total_count})")
    print(f"Full Matches: {correct_count}/{total_count}, Partial Matches (>{partial_match_threshold * 100}% similarity): {partial_count}/{total_count}")
    
    # Save the incorrect queries to a JSON file
    with open('analysis/simple_incorrect.json', 'w') as f:
        json.dump(incorrect_queries, f, indent=4)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SQL Predictions")
    parser.add_argument("--input", type=str, default="predictions/chatgpt_example_then_error.txt", help="Path to the predictions file.")
    parser.add_argument("--dataset_path", type=str, default="../data/validation_sql_ranked.json", help="Path to the dataset file.")
    parser.add_argument("--db_root_path", type=str, default="./data/database", help="Root path to the databases.")
    parser.add_argument("--partial_match_threshold", type=float, default=0.8, help="Threshold for similarity to consider as a partial match.")

    args = parser.parse_args()

    evaluate(args.input, args.dataset_path, args.db_root_path, args.partial_match_threshold)
