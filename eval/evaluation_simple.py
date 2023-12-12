import sqlite3
import json
import os
import argparse
from tqdm import tqdm
import sqlparse
import re
from scripts.helpers import (
    compare_pred_to_gold_on_db,
    compare_pred_to_results_on_db,
    get_result_table_from_db,
    get_error_from_query, 
    find_all_dbs_for_entry,
)
from mo_sql_parsing import parse
from mo_sql_parsing import format as mo_format

def sql_format(text):
    try:
        final_query = text.split("|")[1].strip()
    except Exception:
        final_query = text

    try:
        formatted_query = sqlparse.format(final_query, reindent=True, keyword_case='upper')
    except Exception:
        formatted_query = final_query

    final_query_markdown = f"{formatted_query}"
    return final_query_markdown

def select_repair(incorrect_query, gold_column_names):
    if gold_column_names is None:
        return incorrect_query

    try:
        incorrect_query_json = parse(incorrect_query)
    except Exception as e:
        return incorrect_query

    new_select_clause = []
    for col in gold_column_names:
        if "(" in col and ")" in col:  # Handling aggregate functions
            new_select_clause.append({"value": col, "name": col})
        else:
            new_select_clause.append({"value": col})

    incorrect_query_json['select'] = new_select_clause

    try:
        repaired_query = mo_format(incorrect_query_json)
    except Exception as e:
        return incorrect_query
    
    return repaired_query

def select_flip(incorrect_query):
    # if there are two columns in select, flip them
    try:
        incorrect_query_json = parse(incorrect_query)
    except Exception as e:
        return incorrect_query
    
    select_clause = incorrect_query_json.get('select', {})
    if isinstance(select_clause, list) and len(select_clause) == 2:
        new_select_clause = [select_clause[1], select_clause[0]]
        #print(f"Flipped SELECT: {new_select_clause}")
        incorrect_query_json['select'] = new_select_clause

    try:
        repaired_query = mo_format(incorrect_query_json)
    except Exception as e:
        return incorrect_query
    
    return repaired_query

def groupby_repair(incorrect_query, gold_sql, db_path):
    try:
        incorrect_query_json = parse(incorrect_query)
    except Exception as e:
        return incorrect_query

    # Check if there is a GROUP BY clause
    if 'groupby' in incorrect_query_json:
        # Extract the select clause
        select_clause = incorrect_query_json.get('select', {})

        # Check if select_clause is a list (multiple columns)
        if isinstance(select_clause, list):
            # First, try each column individually
            for col in select_clause:
                if isinstance(col, dict) and 'value' in col:
                    if not isinstance(col['value'], dict):  # Exclude aggregate functions
                        incorrect_query_json['groupby'] = {'value': col['value']}
                        try:
                            repaired_query = mo_format(incorrect_query_json)
                            if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                                return repaired_query
                        except Exception as e:
                            continue
            
            # If individual columns don't work, try using all columns
            all_columns = [col['value'] for col in select_clause if isinstance(col, dict) and 'value' in col and not isinstance(col['value'], dict)]
            if all_columns:
                incorrect_query_json['groupby'] = {'value': all_columns}
                try:
                    repaired_query = mo_format(incorrect_query_json)
                    if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                        return repaired_query
                except Exception as e:
                    pass

    return incorrect_query


def evaluate(input_path, dataset_path, db_root_path, repair, single_index=None):
    with open(input_path, 'r') as f:
        input_queries = [line.strip() for line in f.readlines()]
    
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    with open('analysis/all_entries.json', 'r') as all_entries_f:
        all_entries = json.load(all_entries_f)

    if single_index is not None:
        if 0 <= single_index < len(dataset):
            dataset = [dataset[single_index]]
        else:
            raise ValueError("Provided index is out of dataset range")

    correct_count = 0
    empty_result_count = 0
    total_count = len(dataset)
    incorrect_queries = []

    # Keep repairs count
    select_repair_count = 0
    group_by_repair_count = 0
    select_flip_count = 0

    for idx, entry in tqdm(enumerate(dataset), total=total_count, desc="Evaluating"):
        db_path = os.path.join(db_root_path, entry["db_id"], entry["db_id"] + ".sqlite")

        gold_sql = sql_format(entry['ground_truth'])
        predicted_sql = sql_format(input_queries[single_index] if single_index is not None else input_queries[idx])

        error = get_error_from_query(db_path, predicted_sql)
        
        if error is False:
            pred_cols, pred_results = get_result_table_from_db(db_path, predicted_sql)
            gold_cols, gold_results = get_result_table_from_db(db_path, gold_sql)

            result_empty = True
            if pred_results:
                result_empty = False

            if single_index:
                print(f"\nIndex: {idx}")
                print(f"Question: {entry['question']}")
                print(f'DB_path: {db_path}')
                # print queries
                print(f"Predicted SQL: {predicted_sql}")
                print(f"Gold SQL: {gold_sql}")
                # prints results
                print(f"Predicted Results: {pred_results}")
                print(f"Gold Results: {gold_results}")

            if result_empty:
                empty_result_count += 1
                continue

            match_found = False
            if compare_pred_to_gold_on_db(predicted_sql, gold_sql, db_path):
                match_found = True
                correct_count += 1

            # Try flipping select
            if not match_found and repair:
                repaired_query = select_flip(predicted_sql)
                if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                    print(f"Repaired SELECT by flipping cols: {repaired_query}")
                    match_found = True
                    correct_count += 1
                    select_flip_count += 1

            # Try repair group by
            if not match_found and repair:
                repaired_query = groupby_repair(predicted_sql, gold_sql, db_path)
                if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                    print(f"Repaired GROUP BY: {repaired_query}")
                    match_found = True
                    correct_count += 1
                    group_by_repair_count += 1
            
            #Try repair group by and select flip
            if not match_found and repair:
                repaired_query = select_flip(predicted_sql)
                repaired_query = groupby_repair(repaired_query, gold_sql, db_path)
                if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                    print(f"Repaired SELECT by flipping cols and GROUP BY: {repaired_query}")
                    match_found = True
                    correct_count += 1
                    select_flip_count += 1
                    group_by_repair_count += 1

            # Try repair select
            if not match_found and repair:
                repaired_query = select_repair(predicted_sql, gold_cols)
                if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                    print(f"Repaired SELECT: {repaired_query}")
                    match_found = True
                    correct_count += 1
                    select_repair_count += 1

            # Try repair group by and select
            if not match_found and repair:
                repaired_query = select_repair(predicted_sql, gold_cols)
                repaired_query = groupby_repair(repaired_query, gold_sql, db_path)
                if compare_pred_to_gold_on_db(repaired_query, gold_sql, db_path):
                    print(f"Repaired SELECT and GROUP BY: {repaired_query}")
                    match_found = True
                    correct_count += 1
                    select_repair_count += 1
                    group_by_repair_count += 1

        if not match_found or error:
            incorrect_queries.append({
                'index': idx,
                'difficulty': all_entries[single_index if single_index is not None else idx]['difficulty'],
                'db_id': entry['db_id'],
                'db_info': entry['db_info'],
                'question': entry['question'],
                'pred': predicted_sql,
                'gold': gold_sql,
            })

    accuracy = correct_count / total_count
    print(f"\nAccuracy: {accuracy:.4f} ({correct_count}/{total_count})")
    print(f"Empty Results Count: {empty_result_count}")
    # Print all repairs count in nice format
    if repair:
        print(f"Select Flip Repairs: {select_flip_count}")
        print(f"Select Repairs: {select_repair_count}")
        print(f"Group By Repairs: {group_by_repair_count}")

    with open('analysis/simple_incorrect.json', 'w') as f:
        json.dump(incorrect_queries, f, indent=4)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SQL Predictions")
    parser.add_argument("--input", type=str, default="predictions/chatgpt_example_then_error_best.txt", help="Path to the predictions file.")
    parser.add_argument("--dataset_path", type=str, default="../data/validation_sql_clear.json", help="Path to the dataset file.")
    parser.add_argument("--db_root_path", type=str, default="./data/database", help="Root path to the databases.")
    parser.add_argument("--repair", action="store_true", default=False, help="Whether to perform mutation repair on incorrect queries.")
    parser.add_argument("--index", type=int, default=None, help="Index of the single dataset entry to test")

    args = parser.parse_args()

    evaluate(args.input, args.dataset_path, args.db_root_path, args.repair, args.index)
