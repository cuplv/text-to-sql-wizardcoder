import sqlite3
import json
import os
import argparse
from tqdm import tqdm
import sqlparse
import re
from scripts.helpers import compare_pred_to_gold_on_db, compare_pred_to_results_on_db, get_result_table_from_db, jaccard_similarity, find_all_dbs_for_entry
from itertools import combinations, product
from mo_sql_parsing import parse
from mo_sql_parsing import format as mo_format

def sql_format(text):
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

def perform_select_repair(incorrect_query, gold_column_names):
    if gold_column_names is None:
        return incorrect_query
    # Parse the incorrect SQL query into a JSON structure
    try:
        incorrect_query_json = parse(incorrect_query)
    except Exception as e:
        #print(f"Error parsing SQL query: {e}")
        return incorrect_query

    # Construct the new SELECT clause
    new_select_clause = []
    for col in gold_column_names:
        if "(" in col and ")" in col:  # rudimentary check for aggregate functions
            # Handle as a raw expression
            new_select_clause.append({"value": col, "name": col})
        else:
            new_select_clause.append({"value": col})

    # Replace the SELECT part of the JSON structure
    incorrect_query_json['select'] = new_select_clause

    # Convert the modified JSON back into an SQL query string
    try:
        repaired_query = mo_format(incorrect_query_json)
    except Exception as e:
        #print(f"Error formatting SQL query: {e}")
        return incorrect_query

    return repaired_query


def perform_where_repair(incorrect_query, gold_result, connection):
    cursor = connection.cursor()

    # Parse the incorrect SQL query into JSON structure
    try:
        incorrect_query_json = parse(incorrect_query)
    except Exception as e:
        print(f"Error parsing SQL query: {e}")
        return incorrect_query

    gold_result_size = len(gold_result)

    # Retrieve table information
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    for table_name in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]

        for column in columns:
            quoted_column = f'"{column}"' if not column.isidentifier() or column[0].isdigit() else column
            cursor.execute(f"SELECT DISTINCT {quoted_column} FROM {table_name}")
            distinct_values = [row[0] for row in cursor.fetchall()]

            for value in distinct_values:
                # Define multiple conditions to test
                conditions = [
                    {"eq": [quoted_column, value]}, 
                    {"neq": [quoted_column, value]},
                    {"like": [quoted_column, f'%{value}%']},
                    {"is": [quoted_column, None]},
                    {"is_not": [quoted_column, None]}
                ]

                for condition in conditions:
                    if 'where' in incorrect_query_json:
                        incorrect_query_json['where'] = {"and": [incorrect_query_json['where'], condition]}
                    else:
                        incorrect_query_json['where'] = condition
                
                # Convert the modified JSON back into an SQL query string
                try:
                    return mo_format(incorrect_query_json)
                except Exception as e:
                    #print(f"Error formatting SQL query: {e}")
                    return incorrect_query
             
    return incorrect_query

def evaluate(input, dataset_path, db_root_path, partial_match_threshold, repair):
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

        ground_truth = sql_format(entry['ground_truth'])
        predicted_sql = sql_format(input[idx])

        gt_results = None
        gt_columns = None
        pred_results = None
        pred_columns = None
        non_empty_db_path = None
        for db_path in all_dbs:
            # Try executing the SQL on each database until we get non-empty results
            gt_cols_temp, gt_results_temp = get_result_table_from_db(db_path, ground_truth)
            pred_cols_temp, pred_results_temp = get_result_table_from_db(db_path, predicted_sql)
            
            if gt_results_temp and pred_results_temp and gt_cols_temp and pred_cols_temp:
                gt_results = gt_results_temp
                gt_columns = gt_cols_temp
                pred_results = pred_results_temp
                pred_columns = pred_cols_temp
                non_empty_db_path = db_path
                break

        if not gt_results or not pred_results or not gt_columns or not pred_columns:
            #print(f"Could not find non-empty database for {entry['db_id']}")
            continue

        if compare_pred_to_gold_on_db(predicted_sql, ground_truth, non_empty_db_path):
            correct_count += 1
        else:
            if repair:
                repaired_query = predicted_sql
                connection = sqlite3.connect(non_empty_db_path)
                # Attempt to repair the SELECT clause
                repaired_query_select = perform_select_repair(predicted_sql, gt_columns)
                if compare_pred_to_gold_on_db(repaired_query_select, ground_truth, non_empty_db_path):
                    repaired_query = repaired_query_select
                    print(f"Repaired SELECT clause: {repaired_query_select}")

                # Attempt to repair the WHERE clause
                repaired_query_where = perform_where_repair(repaired_query, gt_results, connection)
                if compare_pred_to_gold_on_db(repaired_query_where, ground_truth, non_empty_db_path):
                    repaired_query = repaired_query_where
                    print(f"Repaired WHERE clause: {repaired_query_where}")
                
                connection.close()

                # Check if any repair worked
                if repaired_query != predicted_sql:
                    correct_count += 1
                    continue

            similarity = jaccard_similarity(set(gt_results), set(pred_results))

            if similarity < partial_match_threshold:
                incorrect_queries.append({
                    'index': idx,
                    'db_id': entry['db_id'],
                    'db_info': entry['db_info'],
                    'question': entry['question'],
                    'predicted_sql': predicted_sql,
                    'ground_truth': ground_truth,
                    'similarity': similarity
                })
            else:
                partial_count += 1

    accuracy = (correct_count + partial_count * 0.5) / total_count
    print(f"\nAccuracy: {accuracy:.4f} ({correct_count + partial_count}/{total_count})")
    print(f"Full Matches: {correct_count}/{total_count}, Partial Matches (>{partial_match_threshold * 100}% similarity): {partial_count}/{total_count}")
    
    # Save the incorrect queries to a JSON file
    with open('analysis/simple_incorrect.json', 'w') as f:
        json.dump(incorrect_queries, f, indent=4)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SQL Predictions")
    parser.add_argument("--input", type=str, default="predictions/chatgpt_example_then_error_best.txt", help="Path to the predictions file.")
    parser.add_argument("--dataset_path", type=str, default="../data/validation_sql_clear.json", help="Path to the dataset file.")
    parser.add_argument("--db_root_path", type=str, default="./data/database", help="Root path to the databases.")
    parser.add_argument("--partial_match_threshold", type=float, default=0.8, help="Threshold for similarity to consider as a partial match.")
    parser.add_argument("--repair", action="store_true", default=False, help="Whether to perform mutation repair on incorrect queries.")

    args = parser.parse_args()

    evaluate(args.input, args.dataset_path, args.db_root_path, args.partial_match_threshold, args.repair)
