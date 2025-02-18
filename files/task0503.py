"""
Solution to 23rd task:
- send password = NONOMNISMORIAR to Rafal's API (/b46c3)
- save received HASH
- 
"""

import requests
import json
import sys
import re
from markdownify import markdownify
from pprint import pp
from time import perf_counter
import threading

from lib.aidevs import send_task_response, get_response
from sekrety import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

rafal_api = f"https://rafal.{central_domain}/b46c3"

ai = MyAI(openai_api_key, False, 10)
model = "gpt-4o-mini"

headers = {"content-type": "application/json"}
data = {"password": "NONOMNISMORIAR"}
response_raw = requests.post(rafal_api, json=data, headers=headers)
response = response_raw.json()
hash = response['message']
data = {"sign": hash}
# Get the signed hash. Now we start fighting against the time.
response_raw = requests.post(rafal_api, json=data, headers=headers)
time_start = perf_counter()
response = response_raw.json()
if response['code'] != 0:
    print("Failed getting the signature!")
    sys.exit(1)
signature = response['message']['signature']
timestamp = response['message']['timestamp']
challenges = response['message']['challenges']
tasks = {}
threads = {}
def get_challenge(challenge):
    global tasks
    global time_start
    tasks[challenge] = {}
    response_raw = requests.get(challenge)
    response = response_raw.json()
    tasks[challenge]['task'] = response['task']
    tasks[challenge]['data'] = response['data']
    print (f"Downloaded challenge {challenge}, time: {perf_counter()-time_start}")
for challenge in challenges:
    threads[challenge] = threading.Thread(target=get_challenge, args=(challenge,))
    threads[challenge].start()
for challenge in challenges:
    threads[challenge].join()
for challenge in challenges:
    page_to_get = re.findall("(https://.*html)", tasks[challenge]['task'])
    if page_to_get:
        page_raw = requests.get(page_to_get[0])
        page_text = page_raw.content.decode('utf8')
        page_nice = markdownify(page_text)
        #page = f"# Contents of webpage {page_to_get[0]} :\n\n{page_nice}"
        page = page_nice
        tasks[challenge]['page'] = page
    else:
        tasks[challenge]['page'] = ""
    tasks[challenge]['answers'] = {}

def get_answer(question, page, challenge, question_num):
    global tasks
    global time_start
    if page:
        system_prompt = f"Please respond user's question giving short and precise answer, with one word or number if possible, using the following knowledge:\n\n{page}"
    else:
        system_prompt = "Please respond user's question using general knowledge, giving short and precise answer, one word or number if possible."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    tasks[challenge]['answers'][question_num] = ai.chat_completion(messages, model, 50, 0)
    print (f"Responded: {challenge} question {question_num}, timestamp: {perf_counter()-time_start}")

threads = {}
for challenge in challenges:
    threads[challenge] = []
    question_num = 0
    for question in tasks[challenge]['data']:
        threads[challenge].append(threading.Thread(target=get_answer, args=(question, tasks[challenge]['page'], challenge, question_num)))
        tasks[challenge]['answers'][question_num] = ""
        question_num += 1
for challenge in challenges:
    for thread in threads[challenge]:
        thread.start()
for challenge in challenges:
    for thread in threads[challenge]:
        thread.join()

answers = []
for challenge in challenges:
    for answer in tasks[challenge]['answers']:
        answers.append(tasks[challenge]['answers'][answer])

data = {
    "apikey": aidevs_api_key,
    "timestamp": timestamp,
    "signature": signature,
    "answer": answers
}
headers = {"content-type": "application/json"}
response_raw = requests.post(rafal_api, json=data, headers=headers)
response = response_raw.json()

print (f"TASK FINISHED IN {perf_counter() - time_start} seconds.")
pp (data, indent=4, width=200)
pp (response, indent=4, width=200)