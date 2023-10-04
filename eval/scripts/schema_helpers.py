import re
import json
import os
from dotenv import load_dotenv
import openai
import time

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_chatgpt(prompt):
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            response_text = response['choices'][0]['message']['content']
            break
            
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            print('Waiting for 5 seconds before retrying...')
            time.sleep(5)
    
    return response_text

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
