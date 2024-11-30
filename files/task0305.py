"""
Solution to 15th task:
- Get users from SQL DB and fill the Graph DB
- Get connections from SQL DB and fill the Graph DB
- Get the shortest path from Rafał to Barbara
- Report the path as a string
"""

import sys
from pprint import pp
from neo4j import GraphDatabase

from lib.aidevs import send_task_response, get_response
from secrets import aidevs_api_key, central_domain, openai_api_key, neo4j_password, neo4j_url
from lib.myai import MyAI

def clearBase(database, silent=False):
    cmd = f"MATCH (n) DETACH DELETE n"
    database.execute_query(cmd)
    if not silent:
        print (cmd)

def addPerson(database, person_name, silent=False):
    cmd = f"CREATE (p:Person {{name:'{person_name}'}})"
    database.execute_query(cmd)
    if not silent:
        print (cmd)

def addConnection(database, person1, person2, silent=False):
    cmd = (
        f"MATCH (a:Person {{name: '{person1}'}}), (b:Person {{name: '{person2}'}})"
        f"MERGE (a)-[:KNOWS]->(b)"
    )
    database.execute_query(cmd)
    if not silent:
        print (cmd)

print (79*"=")
ai = MyAI(openai_api_key, True, 5)
model = "gpt-4o-mini"
task = "connections"
db_task = "database"
database = f"https://centrala.{central_domain}/apidb"
graph_database = GraphDatabase.driver(neo4j_url, auth=("neo4j",neo4j_password))
# Get the database tables
tables_result = get_response(aidevs_api_key, db_task, "show tables", database)
tables = {}
if tables_result['error'] == "OK":
    for entry in tables_result['reply']:
        structure_result = get_response(aidevs_api_key, db_task, f"show create table {entry['Tables_in_banan']}", database)
        if structure_result['error'] == "OK":
            tables[entry['Tables_in_banan']] = structure_result['reply']
        else:
            print (f"Error getting structure for table {entry['Tables_in_banan']}")
            pp (structure_result, indent=4)
else:
    print ("DB reply has an error!")
    pp (tables_result, indent=4)
    sys.exit(1)
print ("\n\nThe list of tables:")
pp(tables, indent=4)
# Generate and execute in SQL prompt for users list
prompt_users = """
Below are the SQL definitions of tables from our database.
Table "users" contains names and ID numbers of different people.
Based on the tables structure, generate SQL query that will return all usernames from table "users".
Please return just the SQL query, without any explanations, thoughts and ornaments. For example: "select a from b where c = d", without any formatting.
"""
for table in tables:
    prompt_users += f"""
## Table "{table}":
{tables[table][0]["Create Table"]}
"""
messages = [{"role": "user", "content": prompt_users}]
response = ai.chat_completion(messages, model, 150, 0)
print (f"\n\nAI response: {response}")
users = get_response(aidevs_api_key, db_task, response, database)
# Generate and execute in SQL prompt for relations
prompt_relations = """
Below are the SQL definitions of tables from our database.
Table "users" contains names and ID numbers of different people.
Table "connections" contains unidirectional relations between the people with two IDs in each record, meaning that person with ID 1 knows person with ID 2.
The IDs in table "connections" relate to user IDs in table "users".
Based on the tables structure, generate SQL query that will return all people relations from "connections" table, but instead of ID 1 and ID 2 - showing the users' names.
Please return just the SQL query, without any explanations, thoughts and ornaments. For example: "select a from b where c = d", without any formatting.
"""
for table in tables:
    prompt_relations += f"""
## Table "{table}":
{tables[table][0]["Create Table"]}
"""
messages = [{"role": "user", "content": prompt_relations}]
response = ai.chat_completion(messages, model, 150, 0)
print (f"\n\nAI response: {response}")
relations = get_response(aidevs_api_key, db_task, response, database)

# Filling the graph database
clearBase(graph_database)   # Clearing old entries first
if users['error'] == "OK":
    for entry in users['reply']:
        addPerson(graph_database, entry['username'])
else:
    print ("There were errors when running the AI-generated query 1:")
    print (response)
    sys.exit(1)
if relations['error'] == "OK":
    for entry in relations['reply']:
        addConnection(graph_database, entry['user1_name'], entry['user2_name'])
else:
    print ("There were errors when running the AI-generated query 2:")
    print (response)
    sys.exit(1)

# Find the connections
cmd = (
    "MATCH p=shortestPath((r:Person {name:'Rafał'})-[*]-(b:Person {name:'Barbara'}))"
    "RETURN nodes(p)"
)
records, summary, keys = graph_database.execute_query(cmd)

pp (records, indent=4, width=200)
pp (summary, indent=4, width=200)
pp (keys, indent=4, width=200)

for record in records:
    print (record['nodes(p)'])

# Prepare the answer string
answer = ""
first_element = True
for record in records[0]['nodes(p)']:
    if not first_element:
        answer += ", "
    answer += record._properties['name']
    first_element = False

print (f"Answer is: {answer}")

# Report to HQ
task_response = send_task_response(aidevs_api_key, task, answer, f"https://centrala.{central_domain}/report")
print ("\n\nFINAL TASK RESPONSE:")
pp (task_response, indent=4)
print (79*"=")
