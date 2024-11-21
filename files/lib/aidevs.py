"""
Simple library to interface with AI devs 3 system
"""

import requests

# Simple function to send the excercise solution to the system and return the confirmation
def send_task_response(api_key, task, answer, response_api = "https://poligon.aidevs.pl/verify"):
    data = {
        "task": task,
        "apikey": api_key,
        "answer": answer
    }
    headers = {"content-type": "application/json"}
    response_raw = requests.post(response_api, json=data, headers=headers)
    return response_raw.json()

def get_response(api_key, task, query, response_api):
    data = {
        "task": task,
        "apikey": api_key,
        "query": query
    }
    headers = {"content-type": "application/json"}
    response_raw = requests.post(response_api, json=data, headers=headers)
    return response_raw.json()
