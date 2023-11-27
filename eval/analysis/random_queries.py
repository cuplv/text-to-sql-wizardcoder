import json
import random

# Load JSON data
with open('incorrect.json') as f:
    json_data = f.read()
data = json.loads(json_data)

# Filter data based on difficulty
extra_difficulty_queries = [item for item in data if item['difficulty'] == 'extra']
hard_difficulty_queries = [item for item in data if item['difficulty'] == 'hard']
medium_difficulty_queries = [item for item in data if item['difficulty'] == 'medium']

# Randomly select the required number of queries
selected_extra_difficulty_queries = random.sample(extra_difficulty_queries, min(15, len(extra_difficulty_queries)))
selected_hard_difficulty_queries = random.sample(hard_difficulty_queries, min(3, len(hard_difficulty_queries)))
selected_medium_difficulty_queries = random.sample(medium_difficulty_queries, min(2, len(medium_difficulty_queries)))

# Combine selected queries
selected_queries = selected_extra_difficulty_queries + selected_hard_difficulty_queries + selected_medium_difficulty_queries

# Write selected queries to file
with open('selected_queries.json', 'w') as f:
    json.dump(selected_queries, f, indent=4)