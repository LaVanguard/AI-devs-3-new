import requests
import re
import sys
import pprint

from lib.aidevs import send_task_response
from secrets import aidevs_api_key

task_name = "POLIGON"
input_link = "https://poligon.aidevs.pl/dane.txt"

print (f"\nOtwieram strone: {input_link}")
input_raw = requests.get(input_link)
input_text = input_raw.content.decode('ascii')
input_values = re.split("\n", input_text)

answer = [i for i in input_values if i]
print ("Odnaleziono wartosci:")
pprint.pp (answer, indent=4)

print (f"Wysylam wartosci do API, zadanie: \"{task_name}\"")
result = send_task_response(aidevs_api_key, task_name, answer)
print (f"Kod odpowiedzi: {result['code']}, odpowiedz: {result['message']}")
