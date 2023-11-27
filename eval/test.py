from mo_sql_parsing import parse, format

def print_query(json_obj, indent=0):
    # Base indent
    base_indent = '    ' * indent

    # If the object is a dictionary
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            print(f"{base_indent}{key}:")
            print_query(value, indent + 1)

    # If the object is a list
    elif isinstance(json_obj, list):
        for item in json_obj:
            print_query(item, indent)

    # If the object is a simple value
    else:
        print(f"{base_indent}{json_obj}")

# Example usage:
sql_query = "SELECT T1.fname , T1.age FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid = T2.stuid JOIN pets AS T3 ON T3.petid = T2.petid WHERE T3.pettype = 'dog' AND T1.stuid NOT IN (SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid = T2.stuid JOIN pets AS T3 ON T3.petid = T2.petid WHERE T3.pettype = 'cat')"

# Example usage:
#sql_query = "SELECT T2.name, T2.capacity FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id = T2.stadium_id WHERE T1.year >= 2014 GROUP BY T2.stadium_id ORDER BY count(*) DESC LIMIT 1"
query_object = parse(sql_query)
formatted_query = format(query_object)

print_query(query_object)
print(formatted_query)

# select:
#     value:
#         T1.fname
#     value:
#         T1.age
# from:
#     value:
#         student
#     name:
#         T1
#     join:
#         value:
#             has_pet
#         name:
#             T2
#     on:
#         eq:
#             T1.stuid
#             T2.stuid
#     join:
#         value:
#             pets
#         name:
#             T3
#     on:
#         eq:
#             T3.petid
#             T2.petid
# where:
#     and:
#         eq:
#             T3.pettype
#             literal:
#                 dog
#         nin:
#             T1.stuid
#             select:
#                 value:
#                     T1.stuid
#             from:
#                 value:
#                     student
#                 name:
#                     T1
#                 join:
#                     value:
#                         has_pet
#                     name:
#                         T2
#                 on:
#                     eq:
#                         T1.stuid
#                         T2.stuid
#                 join:
#                     value:
#                         pets
#                     name:
#                         T3
#                 on:
#                     eq:
#                         T3.petid
#                         T2.petid
#             where:
#                 eq:
#                     T3.pettype
#                     literal:
#                         cat
