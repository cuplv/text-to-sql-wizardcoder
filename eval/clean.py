import re
import sqlparse

def extract_last_sql_query(text):
    # Find all SQL queries in the text
    sql_queries = re.findall(r'```sql\s(.*?)\s```', text, re.DOTALL)

    # Return the last SQL query, or the only one if there's just one
    return sql_queries[-1] if sql_queries else text

def clean_sql_file(input_file, output_file):
    sql_extract_pattern = re.compile(r'```sql(.*?)```', re.DOTALL | re.IGNORECASE)

    with open(input_file, 'r') as file:
        lines = file.readlines()

    cleaned_queries = []
    for line in lines:
        line = line.strip()
        if line:
            # Extract SQL query from the line
            sql_query = extract_last_sql_query(line)

            # Remove comments from the SQL query
            sql_query = sqlparse.format(sql_query, strip_comments=True)

            # Remove newlines from the SQL query
            sql_query = sql_query.replace('\n', ' ')

            # Remove extra spaces from the SQL query
            sql_query = re.sub(r'\s+', ' ', sql_query)

            # Remove trailing semicolon from the SQL query
            sql_query = sql_query.rstrip(';')

            # Add the cleaned SQL query to the list of cleaned queries
            cleaned_queries.append(sql_query)

    with open(output_file, 'w') as file:
        for query in cleaned_queries:
            file.write(query + ';\n')

# Usage
input_file = 'predictions/chatgpt_finetune_example_then_error_gpt4turbo.txt'  # Replace with your input file path
output_file = 'predictions/chatgpt_finetune_example_then_error_gpt4turbo_clean.txt'  # Replace with your desired output file path

clean_sql_file(input_file, output_file)
