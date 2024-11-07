"""
Simple solution to second task.
- get JSON with the data
- go through the entries 1:1
- if object has no questions - just correct maths
- if questions - use AI and correct answer
- send the JSON back
"""

import requests
import json
import re
import sys
from pprint import pp

from secrets import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI
from lib.aidevs import send_task_response

# Define the task source
input_link = f"https://centrala.{central_domain}/data/{aidevs_api_key}/json.txt"
model = "gpt-4o-mini"
ai = MyAI(openai_api_key, True, 1)

# Open the page and get the JSON
print (f"\nOtwieram strone: {input_link}")
input_raw = requests.get(input_link)             # The data is still in binary format
input_text = input_raw.content.decode('utf8')   # Decode from binary to ASCII, still one string
data = json.loads(input_text)
print (f"Dane testowe mają {len(data['test-data'])} elementów.")
data['apikey'] = aidevs_api_key
for index, entry in enumerate(data['test-data']):
    question = re.findall("^(\d+) \+ (\d+)$", entry['question'])
    answer = entry['answer']
    if not question or type(answer) is not int:
        print (f"Entry {index} is bad: {entry}")
        sys.exit(1)
    a = int(question[0][0])
    b = int(question[0][1])
    c = answer
    if a + b != c:
        data['test-data'][index]['answer'] = a + b
        print (f'Index {index}: Corrected "{question}" from {c} to {a+b}.')
    if "test" in entry:
        question = entry['test']['q']
        messages = [
            {"role": "system", "content": "Your task is to respond user's question with just the answer, preferably just one word or one number, without other words or characters."},
            {"role": "user", "content": question}
        ]
        answer = ai.chat_completion(messages, model, 10, 0)
        print (f'Index {index}: Test question "{question}" responded: "{answer}"')
        data['test-data'][index]['test']['a'] = answer
response = send_task_response(aidevs_api_key, "JSON", data, f"https://centrala.{central_domain}/report")
pp (response)
