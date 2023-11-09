from datasets import load_dataset
from tqdm import tqdm
from scripts.helpers import chatgpt, compare_pred_to_gold_on_db, get_result_table_from_db, generate_md_table, get_error_from_query
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import os

def format(response_text):
    response_text = response_text.strip().replace("\n", " ").replace("\t", " ")
    if not response_text.upper().startswith('SELECT'):
        response_text = 'SELECT ' + response_text
    return response_text

def fetch_response(i, entry, args):
    c3_0 = "You are now an excellent SQL writer, first I'll give you some tips and examples, and I need you to remember the tips, and do not make same mistakes."
    c3_1 = """
    Tips 1:
    Question: Which A has most number of B?
    Gold SQL: select A from B group by A order by count ( * ) desc limit 1;
    Notice that the Gold SQL doesn't select COUNT(*) because the question only wants to know the A and the number should be only used in ORDER BY clause, there are many questions asks in this way, and I need you to remember this in the the following questions.
    """
    c3_2 = "Thank you for the tip! I'll keep in mind that when the question only asks for a certain field, I should not include the COUNT(*) in the SELECT statement, but instead use it in the ORDER BY clause to sort the results based on the count of that field."
    c3_3 = """
    Tips 2:
    Don't use "IN", "OR", "LEFT JOIN" as it might cause extra results, use "INTERSECT" or "EXCEPT" instead, and remember to use "DISTINCT" or "LIMIT" when necessary.
    For example,
    Question: Who are the A who have been nominated for both B award and C award?
    Gold SQL should be: select A from X where award = 'B' intersect select A from X where award = 'C';
    """
    c3_4 = """Thank you for the tip! I'll remember to use "INTERSECT" or "EXCEPT" instead of "IN", "NOT IN", or "LEFT JOIN" when I want to find records that match or don't match across two tables. Additionally, I'll make sure to use "DISTINCT" or "LIMIT" when necessary to avoid repetitive results or limit the number of results returned."""

    prompt = f"""
    ### Complete sqlite SQL query only and with no explanation, and do not select extra columns that are not explicitly requested in the query.
    ### Sqlite SQL tables, with their properties:
    #
    {entry['db_info']}
    #
    ### {entry['question']}
    SELECT
    """

    # Define messages to keep track of the message history
    messages = [
        {"role": "system", "content": c3_0},
        {"role": "user", "content": c3_1},
        {"role": "assistant", "content": c3_2},
        {"role": "user", "content": c3_3},
        {"role": "assistant", "content": c3_4},
        {"role": "user", "content": prompt}
    ]
    
    response_text = format(chatgpt(messages, model='ft:gpt-3.5-turbo-1106:personal::8I4lPX45'))
    messages.append({"role": "assistant", "content": response_text})

    db = os.path.join('./data/database', entry["db_id"], entry["db_id"] + ".sqlite")
    #db_code = generate_dummy_db(entry['db_info'], entry['question'])

    ## Example driven error correction
    if args.example_driven:
        if not compare_pred_to_gold_on_db(response_text, entry['ground_truth'], db):
            print(f'Example Correcting: {i}')
            cols, results = get_result_table_from_db(db, entry['ground_truth'])
            md_table = None
            if (cols, results) != (None, None):
                md_table = generate_md_table(cols, results)

            new_prompt = f"""That is incorrect. Please try again. The resulting table from the query is not what it should be. The correct result table is below. Don't try to match exactly to the result table I give, I want these to work for any content in a larger database. Please try to fix you original query as best you can with the new information.
            ### Complete sqlite SQL query only and with no explanation, and do not select extra columns that are not explicitly requested in the query.
            ### Correct dummy result table: 
            #
            {md_table}
            #
            ### {entry['question']}
            SELECT
            """
            
            messages.append({"role": "user", "content": new_prompt})
            response_text = format(chatgpt(messages, model='ft:gpt-3.5-turbo-1106:personal::8I4lPX45'))
            #print(messages)
            #print(response_text)
            messages.append({"role": "assistant", "content": response_text})

    ## Error correction given the error
    if args.error_driven:
        if not compare_pred_to_gold_on_db(response_text, entry['ground_truth'], db):
            result_table = get_result_table_from_db(db, response_text)
            error = None
            if result_table == (None, None):
                err_str = get_error_from_query(response_text, db)
                error = f"""
                ### Error in the SQL when executed on a dummy database:
                #
                # {err_str}
                #
                """

            print(f'Error Correcting: {i}')
            new_prompt = f"""
            ##### Fix bugs in the below SQL for the given question.
            ### Sqlite SQL tables, with their properties:
            #
            {entry['db_info']}
            #
            {error}
            ### {entry['question']}
            ### Buggy SQL:
            {response_text}
            ### Fixed SQL:
            SELECT
            """
            #print(new_prompt)
            #messages.append({"role": "user", "content": new_prompt})
            messages.clear()
            messages.append({"role": "user", "content": new_prompt})
            response_text = format(chatgpt(messages, model='gpt-4'))
            messages.append({"role": "assistant", "content": response_text})

    return i, response_text

def main(args):
    with open('../data/validation_sql_ranked.json', 'r') as f:
        dataset = json.load(f)

    responses = {}
    # Using ThreadPoolExecutor to parallelize the work
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(fetch_response, i, entry, args) for i, entry in enumerate(dataset)]
        for future in tqdm(as_completed(futures), total=len(dataset), desc="Generating responses"):
            idx, response_text = future.result()
            responses[idx] = response_text

    # Sort responses by index and then write to the file
    sorted_responses = [responses[i] for i in sorted(responses.keys())]

    with open(args.output, 'a') as f:
        for response_text in sorted_responses:
            f.write(response_text + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate SQL queries using ChatGPT.')
    parser.add_argument('--output', type=str, default='predictions/chatgpt_few_shot.txt', help="Output file path.")
    parser.add_argument('--example_driven', action='store_true', default=False, help="Use example driven correction.")
    parser.add_argument('--error_driven', action='store_true', default=False, help="Use error correction.")
    parser.add_argument('--threads', type=int, default=8, help="Number of threads to use.")
    args = parser.parse_args()
    main(args)

