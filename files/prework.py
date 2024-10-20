"""
First (and only) pre-work solution.
- open the given link
- get 2 strings from the page
- post the strings in pre-defined JSON structure to AI devs API
The API key needs to be defined in secrets.py file.
"""
import requests
import re
import sys
import pprint

from lib.aidevs import send_task_response
from secrets import aidevs_api_key

# Define the task parameters
task_name = "POLIGON"
input_link = "https://poligon.aidevs.pl/dane.txt"

# Open the page and get the strings
print (f"\nOtwieram strone: {input_link}")
input_raw = requests.get(input_link)             # The data is still in binary format
input_text = input_raw.content.decode('ascii')   # Decode from binary to ASCII, still one string
input_values = re.split("\n", input_text)        # Split the string by lines; last line will be empty!
answer = [i for i in input_values if i]          # nice way of filling the array skipping the last empty line
print ("Odnaleziono wartosci:")
pprint.pp (answer, indent=4)
# Send the strings to API (using send_task_response)
print (f"Wysylam wartosci do API, zadanie: \"{task_name}\"")
result = send_task_response(aidevs_api_key, task_name, answer)
print (f"Kod odpowiedzi: {result['code']}, odpowiedz: {result['message']}")
