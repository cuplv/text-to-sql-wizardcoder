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
    pattern = r'```(?:\w+)?\s?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]

def generate_dummy_db(db_info, question, query):
    pre_prompt = "Generate a SQLite database with dummy data for this database, output the SQL code in a SQL code block. Make sure you add dummy data relevant to the question and query.\n\n"
    prompt = pre_prompt + db_info + "\n\nQuestion: " + question + "\nQuery: " + query

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
            print('Waiting for 20 seconds before retrying...')
            time.sleep(20)

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
        print(cursor.fetchall())

        # Close the connection
        conn.close()

        # If everything executed without errors, return True
        return True

    except Exception as e:
        print(f"Error encountered: {e}")
        return False

db_info = """| singer: country, age, singer_id, name, song_name, song_release_year | concert: concert_id | stadium: stadium_id | singer_in_concert: singer_id, concert_id | singer_in_concert.singer_id = singer.singer_id | singer_in_concert.concert_id = concert.concert_id | concert.stadium_id = stadium.stadium_id |"""
question = "What is the average, minimum, and maximum age for all French singers?"
query = """select avg ( age ) , min ( age ) , max ( age ) from singer where country = 'France'"""

db_code = generate_dummy_db(db_info, question, query)
testbool = test_query_on_dummy_db(db_code, query)
print(testbool)
