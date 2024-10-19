import requests
import re
import sys

from secrets import aidevs_api_key

from lib.aidevs import send_task_response

input_link = "https://poligon.aidevs.pl/dane.txt"
task_name = "POLIGON"

print (f"Otwieram strone: {input_link}")
input_raw = requests.get(input_link)
input_text = input_raw.content.decode('ascii')
input_values = re.split("\n", input_text)

print ("Odnaleziono wartosci:")
answer = []
for i in input_values:
    if i:
        print (f"  {i}")
        answer.append(i)

print (f"Wysylam wartosci do API, zadanie: \"{task_name}\"")

result = send_task_response(aidevs_api_key, task_name, answer)

print (f"Kod odpowiedzi: {result['code']}, odpowiedz: {result['message']}")