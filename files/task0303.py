"""
Solution to task 13
- Get Tables from database
- Get tables' structure
- Pass structure to AI, asking to write the final query
- get the answers
"""

import sys
from pprint import pp

from lib.aidevs import send_task_response, get_response
from secrets import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI
print (79*"=")
ai = MyAI(openai_api_key, True, 5)
model = "gpt-4o-mini"
task = "database"
database = f"https://centrala.{central_domain}/apidb"
# Get the database tables
tables_result = get_response(aidevs_api_key, task, "show tables", database)
tables = {}
if tables_result['error'] == "OK":
    for entry in tables_result['reply']:
        structure_result = get_response(aidevs_api_key, task, f"show create table {entry['Tables_in_banan']}", database)
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
# Generate prompt
prompt = """
Below are the SQL definitions of tables from our database.
Based on the tables structure, generate SQL query that will get from the database all active datacenters (DC_ID) that are managed by employees, who are on vacation (is_active=0).
Please return just the SQL query, without any explanations, thoughts and ornaments. For example: "select a from b where c = d", without any formatting.
"""
for table in tables:
    prompt += f"""
## Table "{table}":
{tables[table][0]["Create Table"]}
"""
# print (prompt)
messages = [{"role": "user", "content": prompt}]
response = ai.chat_completion(messages, model, 150, 0)
print (f"\n\nAI response: {response}")
answers = get_response(aidevs_api_key, task, response, database)
answer = []
if answers['error'] == "OK":
    for entry in answers['reply']:
        answer.append(entry['dc_id'])
else:
    print ("There were errors when running the AI-generated query:")
    pp (answers, indent=4)
    sys.exit(1)
print ("\n\nThe answers are:")
pp (answer, indent=4)
task_response = send_task_response(aidevs_api_key, task, answer, f"https://centrala.{central_domain}/report")
print ("\n\nFINAL TASK RESPONSE:")
pp (task_response, indent=4)
print (79*"=")
