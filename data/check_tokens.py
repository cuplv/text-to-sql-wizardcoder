import json

# Load the json data
with open('train_sql_skeleton.json') as f:
    data = json.load(f)

# Initial longest token count is 0
longest_token_count = 0

# Initial total token count is 0
total_token_count = 0

longest_text = ""

for item in data:
    # Get the 'train_instruct' field
    train_instruct = item['text']
    
    # Calculate the token count by dividing the character count by 3.6 and rounding up
    token_count = round(len(train_instruct) / 3.6)
    
    # Add the token count to the total
    total_token_count += token_count

    # If this token count is the longest, update longest_token_count
    if token_count > longest_token_count:
        longest_token_count = token_count
        longest_text = train_instruct

# Calculate the average token count
average_token_count = total_token_count / len(data)

print(f"The longest token count for 'train_instruct' in the dataset is {longest_token_count}.")
print(f"The average token count for 'train_instruct' in the dataset is {average_token_count}.")
print(f"The longest text for 'train_instruct' in the dataset is {longest_text}.")
