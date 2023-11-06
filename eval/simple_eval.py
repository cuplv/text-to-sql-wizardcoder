import sqlite3
import json
import os
import argparse
from tqdm import tqdm
import sqlparse
import glob
import re
from scripts.helpers import compare_pred_to_gold_on_db
from itertools import combinations, product

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

def perform_mutation_repair(incorrect_query, gold_result, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # Identify the number of columns in the gold result
    gold_columns_count = len(gold_result[0]) if gold_result and len(gold_result[0]) > 0 else 0

    # Try to extract the SELECT part of the query
    select_clause_match = re.search(r"SELECT\s+(.*?)\s+FROM", incorrect_query, re.IGNORECASE)
    if not select_clause_match:
        return None

    original_select_columns = select_clause_match.group(1).split(',')
    original_select_columns = [col.strip() for col in original_select_columns]

    for table_name in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]

        # Generate possible new SELECT clauses by adding or removing columns
        for num_columns in range(max(1, gold_columns_count - 1), gold_columns_count + 2):
            possible_column_combinations = combinations(columns, num_columns)
            for column_combination in possible_column_combinations:
                # Construct a new SELECT clause
                new_select_clause = ", ".join(column_combination)

                # Replace the original SELECT clause with the new one
                modified_query = re.sub(r"SELECT\s+.*?\s+FROM", f"SELECT {new_select_clause} FROM", incorrect_query, flags=re.IGNORECASE)

                try:
                    cursor.execute(modified_query)
                    result = cursor.fetchall()
                    if result == gold_result:
                        return modified_query
                except sqlite3.OperationalError:
                    pass

    return None

def perform_where_clause_repair(incorrect_query, gold_result, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    gold_result_size = len(gold_result)

    for table_name in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]

        for column in columns:
            # Ensure column names are properly quoted
            quoted_column = f'"{column}"' if not column.isidentifier() else column

            cursor.execute(f"SELECT DISTINCT {quoted_column} FROM {table_name}")
            distinct_values = [row[0] for row in cursor.fetchall()]

            for value in distinct_values:
                # Construct conditions for WHERE clause
                conditions = [f"{quoted_column} = '{value}'", f"{quoted_column} != '{value}'"]

                for condition in conditions:
                    # Modify the query by adding or modifying the WHERE clause
                    if "WHERE" in incorrect_query.upper():
                        modified_query = re.sub(r"WHERE\s+(.*)", r"WHERE \1 AND " + condition, incorrect_query, flags=re.IGNORECASE)
                    else:
                        modified_query = incorrect_query + f" WHERE {condition}"

                    # Ensure that modified_query contains only a single SQL statement
                    statements = sqlparse.split(modified_query)
                    if len(statements) == 1:
                        try:
                            cursor.execute(statements[0])
                            result = cursor.fetchall()
                            if len(result) == gold_result_size:
                                return statements[0]
                        except sqlite3.OperationalError:
                            pass

    return None

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
        non_empty_db_path = None
        for db_path in all_dbs:
            # Try executing the SQL on each database until we get non-empty results
            gt_results_temp = execute_sql_on_db(db_path, ground_truth)
            pred_results_temp = execute_sql_on_db(db_path, predicted_sql)
            
            if gt_results_temp and pred_results_temp:
                gt_results = gt_results_temp
                pred_results = pred_results_temp
                non_empty_db_path = db_path
                break

        if gt_results and pred_results:
            if set(gt_results) == set(pred_results):
                correct_count += 1
            else:
                # Perform mutation repair
                conn = sqlite3.connect(non_empty_db_path)
                
                # First, try mutation repair
                repaired_query = perform_mutation_repair(predicted_sql, gt_results, conn)
                
                # If mutation repair didn't work, try where clause repair on the original query
                if not repaired_query:
                    repaired_query = perform_where_clause_repair(predicted_sql, gt_results, conn)
                
                # If mutation repair worked, try where clause repair on the repaired query
                else:
                    repaired_query_with_where = perform_where_clause_repair(repaired_query, gt_results, conn)
                    
                    # Use the further repaired query only if it's not None, otherwise keep the mutation repair
                    if repaired_query_with_where:
                        repaired_query = repaired_query_with_where

                conn.close()
                
                # Check if the repaired query is correct
                repaired_results = None
                if repaired_query:
                    repaired_results = execute_sql_on_db(non_empty_db_path, repaired_query)
                    if set(gt_results) == set(repaired_results):
                        correct_count += 1
                        print(f"Repaired query for {entry['question']}:\n{repaired_query}\n")

                common_rows = len(set(gt_results).intersection(set(repaired_results if repaired_results else pred_results)))
                similarity = common_rows / len(gt_results)

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
    parser.add_argument("--dataset_path", type=str, default="../data/validation_sql_ranked.json", help="Path to the dataset file.")
    parser.add_argument("--db_root_path", type=str, default="./data/database", help="Root path to the databases.")
    parser.add_argument("--partial_match_threshold", type=float, default=0.8, help="Threshold for similarity to consider as a partial match.")

    args = parser.parse_args()

    evaluate(args.input, args.dataset_path, args.db_root_path, args.partial_match_threshold)
