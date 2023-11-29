import re
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
import sqlite3
import sqlparse
import time
import glob


# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("OPENAI_ORG_ID"))

def chatgpt(messages, model='ft:gpt-3.5-turbo-1106:personal::8I4lPX45'):
    for i in range(5):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                timeout=60
            )

            return response.choices[0].message.content
        
        except requests.exceptions.Timeout:
            print(f'Timeout occurred on attempt {i+1}')
            print('Retrying...')
            time.sleep(5)
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            print('Retrying...')
            model='ft:gpt-3.5-turbo-1106:personal::8I4lPX45'
            time.sleep(5)
                
    # all retries have failed.
    print("All retries failed for chatgpt.")
    return "###"

def extract_json_object(text):
    # Match content inside {} which looks like a JSON object
    matches = re.findall(r'({.*?})', text, re.DOTALL)
    
    # Try to load each match as a JSON object and return the first successful one
    for match in matches:
        try:
            json_obj = json.loads(match)
            return json_obj
        except json.JSONDecodeError:
            continue
    return None

def extract_list_object(text):
    # Match content inside [], and handle multi-line content using the DOTALL flag
    matches = re.findall(r'\[(.*?)\]', text, re.DOTALL)
    
    # Extracting comma separated values from matches and converting them to a list
    values = []
    for match in matches:
        values.extend([item.strip() for item in match.split(",")])

    # remove extra "" from values
    values = [value.strip('"') for value in values]
        
    return values

def reorder_tables(schema_str, rank_list):
    if not rank_list:
        return schema_str
    # Split the schema string by '#' to get individual table definitions
    tables = [table.strip() for table in schema_str.split('#') if table.strip() and '(' in table]
    relationships = [relation.strip() for relation in schema_str.split('#') if relation.strip() and '=' in relation]

    # Create a mapping of table name to its definition
    table_map = {table.split('(')[0].strip(): table for table in tables}

    # Fetch the definitions based on the rank list
    reordered_tables = ['# ' + table_map[table_name] for table_name in rank_list if table_name in table_map]

    # Filter out the relationships that refer to tables not in the rank list
    filtered_relationships = []
    for relation in relationships:
        left_side, right_side = relation.split('=')
        if all(table_name in rank_list for table_name in [left_side.split('.')[0].strip(), right_side.split('.')[0].strip()]):
            filtered_relationships.append('# ' + relation)
    
    # Concatenate the reordered tables and filtered relationships, adding newlines between them
    result = '\n'.join(reordered_tables + filtered_relationships)
    
    return result

def split_table_definition(table_def):
    """Split table definition to get table name and columns string."""
    depth = 0
    for i, char in enumerate(table_def):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        # When the first opening parenthesis at root level is encountered
        if depth == 1 and char == '(':
            start_idx = i
        # Match the root level closing parenthesis
        elif depth == 0 and char == ')':
            end_idx = i
            break

    return table_def[:start_idx].strip(), table_def[start_idx+1:end_idx].strip()

def reorder_columns(schema_str, rank_dict):
    if not rank_dict:
        return schema_str

    # Split the schema string by '#' to get individual table definitions and relationships
    tables = [table.strip() for table in schema_str.split('#') if table.strip() and '(' in table]
    relationships = [relation.strip() for relation in schema_str.split('#') if relation.strip() and '=' in relation]

    reordered_tables = []
    
    for table in tables:
        table_name, columns_str = split_table_definition(table)
        
        if table_name in rank_dict:
            if rank_dict[table_name]:  # Check if column list is non-empty
                # Extract columns and reorder them
                columns = [col.split()[0].strip() for col in columns_str.split(',')]
                ordered_columns = [col for col in rank_dict[table_name] if col in columns]
                reordered_table = table_name + ' ( ' + ', '.join(ordered_columns) + ' )'
                reordered_tables.append('# ' + reordered_table)

    # Filter out the relationships that refer to tables not in the rank dict
    filtered_relationships = []
    for relation in relationships:
        left_side, right_side = relation.split('=')
        left_table = left_side.split('.')[0].strip()
        right_table = right_side.split('.')[0].strip()
        
        if (left_table in rank_dict and rank_dict[left_table]) and (right_table in rank_dict and rank_dict[right_table]):
            filtered_relationships.append('# ' + relation)
    
    # Concatenate the reordered tables and filtered relationships, adding newlines between them
    result = '\n'.join(reordered_tables + filtered_relationships)
    
    return result

def extract_db_code(text):
    text = text.replace(".print", "")
    pattern = r'```(?:\w+)?\s?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]

# def generate_dummy_db(db_info, question):
#     pre_prompt = """
#     Generate a SQLite database with dummy data for this database from the DB Layout. Your task is to generate just a database, no queries. For each input do the following:
#         1. Breakdown the Question into small pieces and explain what the question is asking for.
#         2. Write code to create the specified dummy database using the same exact table and column names used from the DB Layout. Insert dummy data relevant to the Question. Output the datbase code in a single code block. Don't write any queries or SELECT statements in the code.
#     """
#     prompt = pre_prompt + "\n\nDB Layout:" + db_info + "\n\nQuestion: " + question

#     response_text = ask_chatgpt(prompt)
#     db_code = extract_db_code(response_text)
#     return db_code

# def test_query_on_dummy_db(db_code, query):
#     try:
#         # Connect to an SQLite database in memory
#         conn = sqlite3.connect(':memory:')
#         cursor = conn.cursor()

#         # Iterate over each extracted SQL block and split them into individual commands
#         for sql_block in db_code:
#             statements = sqlparse.split(sql_block)
            
#             # Execute each SQL command
#             for statement in statements:
#                 if statement:
#                     cursor.execute(statement)

#         # Run the provided test query against the database
#         cursor.execute(query)
#         print(f"Query: {query}\tResult: {cursor.fetchall()}")

#         # Close the connection
#         conn.close()

#         # If everything executed without errors, return True
#         return True

#     except Exception as e:
#         print(f"Query: {query}\tError encountered: {e}")
#         return False

# def compare_pred_to_gold(pred_query, gold_query, db_code):
#     try:
#         # Connect to an SQLite database in memory
#         conn = sqlite3.connect(':memory:')
#         cursor = conn.cursor()

#         # Iterate over each extracted SQL block and split them into individual commands
#         for sql_block in db_code:
#             statements = sqlparse.split(sql_block)
            
#             # Execute each SQL command
#             for statement in statements:
#                 if statement:
#                     cursor.execute(statement)

#         # Run the provided test query against the database
#         cursor.execute(pred_query)
#         pred_result = cursor.fetchall()

#         cursor.execute(gold_query)
#         gold_result = cursor.fetchall()

#         # Close the connection
#         conn.close()

#         print(f"pred: {pred_result}\ngold: {pred_result}\nequal: {pred_result == gold_result}")

#         # If everything executed without errors, return True
#         return pred_result == gold_result

#     except Exception as e:
#         print(f"Query: {pred_query}\tError encountered: {e}")
#         return False
    
# def get_result_table(db_code, query):
#     try:
#         # Connect to an SQLite database in memory
#         conn = sqlite3.connect(':memory:')
#         cursor = conn.cursor()

#         # Iterate over each extracted SQL block and split them into individual commands
#         for sql_block in db_code:
#             statements = sqlparse.split(sql_block)
            
#             # Execute each SQL command
#             for statement in statements:
#                 if statement:
#                     cursor.execute(statement)

#         # Run the provided test query against the database
#         cursor.execute(query)
#         result = cursor.fetchall()

#         # Close the connection
#         conn.close()

#         # If everything executed without errors, return True
#         return result

#     except Exception as e:
#         print(f"Query: {query}\tError encountered: {e}")
#         return e
    
def get_schema(db):
    schema = {}
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # fetch table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [str(table[0].lower()) for table in cursor.fetchall()]

    # fetch table info
    for table in tables:
        cursor.execute("PRAGMA table_info({})".format(table))
        schema[table] = [str(col[1].lower()) for col in cursor.fetchall()]

    return schema

def get_result_table_from_db(db, query):
    try:
        # Connect to an SQLite database in memory
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Run the provided test query against the database
        cursor.execute(query)
        
        # Fetch column names
        columns = [column[0].lower() for column in cursor.description]
        
        result = cursor.fetchall()

        # Close the connection
        conn.close()

        # Return column names along with results
        return columns, result

    except Exception as e:
        #print(f"Query: {query}\tError encountered: {e}")
        return None, None
    
def get_error_from_query(db, query):
    try:
        # Connect to an SQLite database in memory
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Run the provided test query against the database
        cursor.execute(query)
        
        # Fetch column names
        columns = [column[0].lower() for column in cursor.description]
        
        result = cursor.fetchall()

        # Close the connection
        conn.close()

        # Return column names along with results
        return columns, result

    except Exception as e:
        #print(f"Query: {query}\tError encountered: {e}")
        return e
    
def generate_md_table(cols, results):
    # Create table header
    if not cols:
        return "No results"
    
    header = '| ' + ' | '.join(cols) + ' |'
    
    # Create separator
    separator = '| ' + ' | '.join(['---' for col in cols]) + ' |'
    
    # Create rows
    rows = []
    for result in results:
        row = '| ' + ' | '.join([str(item) for item in result]) + ' |'
        rows.append(row)
    
    # Combine header, separator, and rows
    table = '\n'.join([header, separator] + rows)
    return table

    
def compare_pred_to_gold_on_db(pred_query, gold_query, db):
    try:
        # Connect to an SQLite database in memory
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Run the provided test query against the database
        cursor.execute(pred_query)
        pred_result = cursor.fetchall()

        cursor.execute(gold_query)
        gold_result = cursor.fetchall()

        # Close the connection
        conn.close()

        #print(f"pred: {pred_result}\ngold: {gold_result}\nequal: {pred_result == gold_result}")

        # If everything executed without errors, return True
        return pred_result == gold_result

    except Exception as e:
        #print(f"equal: false\n{e}")
        return False
    
def compare_pred_to_results_on_db(pred_query, gold_results, db):
    try:
        # Connect to an SQLite database in memory
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Run the provided test query against the database
        cursor.execute(pred_query)
        pred_result = cursor.fetchall()

        # Close the connection
        conn.close()

        #print(f"pred: {pred_result}\ngold: {pred_result}\nequal: {pred_result == gold_result}")

        # If everything executed without errors, return True
        return pred_result == gold_results

    except Exception as e:
        #print(f"equal: false\n{e}")
        return False
    
def jaccard_similarity(set1, set2):
    # Calculate the Jaccard similarity coefficient between two sets
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def find_all_dbs_for_entry(db_folder):
    return glob.glob(os.path.join(db_folder, "*.sqlite"))
    

# schema_str = """
# # stadium ( stadium_id , location , name , capacity default (10 + (5 * 2)) , highest , lowest , average )
# # singer ( singer_id , name , country , song_name , song_release_year , age , is_male )
# # concert ( concert_id , concert_name , theme , stadium_id , year )
# # singer_in_concert ( concert_id , singer_id )
# # concert.stadium_id = stadium.stadium_id
# # singer_in_concert.singer_id = singer.singer_id
# # singer_in_concert.concert_id = concert.concert_id
# """

# rank_dict = {
#     'singer': ['name', 'singer_id', 'country'],
#     'concert': None,
#     'singer_in_concert': ['singer_id', 'concert_id'],
#     'stadium': ['name', 'location', 'capacity', 'average']
# }

# print(reorder_columns(schema_str, rank_dict))
