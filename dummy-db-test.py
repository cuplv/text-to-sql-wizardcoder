import sqlite3
import sqlparse
import re
import time
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_db_code(text):
    print(text)
    text = text.replace(".print", "")
    pattern = r'```(?:\w+)?\s?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]

def extract_from_code_block(text):
    # First try to match text inside ```
    pattern = r'```(?:\w+)?\s?(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If no match in ```, try to match SQL-like text
    pattern = r'\((SELECT .*?)\)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Return None if no match found
    return ""

def generate_dummy_db(db_info, question):
    pre_prompt = """
    Generate a SQLite database with dummy data for this database from the DB Layout. Your task is to generate just a database, no queries. For each input do the following:
        1. Breakdown the Question into small pieces and explain what the question is asking for.
        2. Write code to create the specified dummy database using the same exact table and column names used from the DB Layout. Insert dummy data relevant to the Question. Output the datbase code in a single code block. Don't write any queries or SELECT statements in the code.
    """
    prompt = pre_prompt + "\n\nDB Layout:" + db_info + "\n\nQuestion: " + question

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                #temperature=0.7,
            )
            response_text = response['choices'][0]['message']['content']
            
            db_code = extract_db_code(response_text)

            return db_code
            
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            print('Waiting for 10 seconds before retrying...')
            time.sleep(10)

def test_query_on_dummy_db(db_code, query):
    try:
        # Connect to an SQLite database in memory
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        # Iterate over each extracted SQL block and split them into individual commands
        for sql_block in db_code:
            statements = sqlparse.split(sql_block)
            
            # Execute each SQL command
            for statement in statements:
                if statement:
                    cursor.execute(statement)

        # Run the provided test query against the database
        cursor.execute(query)
        print(f"Query: {query}\tResult: {cursor.fetchall()}")

        # Close the connection
        conn.close()

        # If everything executed without errors, return True
        return True

    except Exception as e:
        print(f"Query: {query}\tError encountered: {e}")
        return False

def choose_best_query(queries, question):
    pre_prompt = """
    Given a list of queries. Your task is to choose just a single query which satisfies the question the most with the least amount of filters, groupings, and conditions. For each input do the following:
        1. Breakdown the list of queries into small pieces and explain what each query is doing.
        2. Breakdown the question peice by piece and explain what each part of the question is asking for. If asking to order by, pay close attention to which order the question is asking for.
        3. Output the most relevant query to the question in a single markdown code block.
    """
    prompt = pre_prompt + "\n\nQuestion: " + question + "\n\nQueries:" + "\n\n".join(queries)

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                #temperature=0.7,
            )
            response_text = response['choices'][0]['message']['content']
            print(response_text)
            
            query = extract_from_code_block(response_text)

            return query
            
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            print('Waiting for 10 seconds before retrying...')
            time.sleep(10)
    

db_info = """| singer: name, country, age, singer_id, song_name, song_release_year, is_male | singer_in_concert: singer_id, concert_id | concert: concert_id, concert_name, theme, stadium_id, year | stadium: stadium_id, location, name, capacity, highest, lowest, average |"""
question = "Show name, country, age for all singers ordered by age from the oldest to the youngest."
queries = [
    """SELECT name, country, age FROM singer ORDER BY age ASC""",
    """SELECT name, country, age FROM singer ORDER BY age ASC""",
    """SELECT name, country, age FROM singer ORDER BY age DESC""",
    """SELECT name, country, age FROM singer ORDER BY age ASC""",
]

db_code = generate_dummy_db(db_info, question)
for query in queries:
    testbool = test_query_on_dummy_db(db_code, query)
query = choose_best_query(queries, question)
print("Best query: " + query)
