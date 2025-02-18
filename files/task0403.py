"""
Solution to 18th task:
- Get questions from HQ
- For each - go through website following most "logical" links, until answer is found
- Return answers to HQ :)
(main part - function to iteratively browse website looking for an answer)
"""

import requests
import json
import os
import re
import sys
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from pprint import pp

from lib.aidevs import send_task_response
from sekrety import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

print (79*"=")
ai = MyAI(openai_api_key, False, 5)
model = "gpt-4o"
task = "softo"
questions_page = f"https://centrala.{central_domain}/data/{aidevs_api_key}/softo.json"
softo_page = f"https://softo.{central_domain}"

# Function to get answer from website or to give a link to follow
prompt = f"""
You are a bot created to find answer to a specific question on a website.
Please send your reply in JSON format, sending a directory with 2 keys: "answer" and "get".
If the answer to the question is available on the page, please respond with the answer - put the answer as the "answer" value in JSON object and leave the "get" value empty.
If you don't find the answer on the opened pages, please find a URL link to the page that is most likely to have the answer (avoiding the pages that were already opened). Return the URL in the "get" value in the JSON object, leaving the "answer" value empty.
The website main page address is: {softo_page}

The question you need to find answer to is:
<question>
"""
def get_answer(question):
    messages = [
        {"role": "system", "content": f"{prompt}\n{question}"}
    ]
    for i in range(10):
        result_raw = ai.chat_completion_json(messages, model, 200, 0, "Web crawler")
        result = json.loads(result_raw)
        if result['answer']:
            return result['answer']
        messages.append({"role": "assistant", "content": result_raw})
        print (f"\n\nAI: {result_raw}")
        try:
            page_raw = requests.get(result['get'])
        except Exception as error:
            print (f"Error in GET request: {error}")
            sys.exit(1)
        page_text = page_raw.content.decode('utf8')
        page_markdown = md(page_text)
        message = f"Page {result['get']} :\n{page_markdown}"
        messages.append({"role": "user", "content": message})

# Get questions from JSON
try:
    questions_raw = requests.get(questions_page)
except Exception as error:
    print (f"Error in GET request: {error}")
    sys.exit(1)
questions_text = questions_raw.content.decode('utf8')
questions = json.loads(questions_text)

# Answer the questions
answers = {}
for question in questions:
    print (79*"=")
    print (f"Question {question}: {questions[question]}")
    answers[question] = get_answer(questions[question])
    print (f"Answer: {answers[question]}")

final_response = send_task_response(aidevs_api_key, task, answers, f"https://centrala.{central_domain}/report")
pp (final_response, indent=4, width=200)
