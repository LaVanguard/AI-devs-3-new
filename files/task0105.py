"""
Solution to 5th task.
- Get the original text from data server
- Pass the text to local Ollama for anonimization
- Send the censored text to Centrala
"""
import requests
import json
from pprint import pp

from lib.aidevs import send_task_response
from sekrety import local_ollama_server, aidevs_api_key, central_domain

# Open the task source page and get the data to anonimize
input_link = f"https://centrala.{central_domain}/data/{aidevs_api_key}/cenzura.txt"
print (f"\nOtwieram strone: {input_link}")
input_raw = requests.get(input_link)             # The data is still in binary format
input_text = input_raw.content.decode('utf8')   # Decode from binary to ASCII, still one string
print ("The input text is:")
print (input_text)
prompt = """
Your task is to modify the original text and re-write it with selected parts replaced by the word "CENZURA":
- Where the text mentions a first name and a surname, it should be replaced by one "CENZURA" word (one "CENZURA" replaces the whole name)
- Where the text mentions a street address, it should be replaced by "CENZURA" (replacing street name and the number)
- Where the text mentions a city name, it should be replaced by "CENZURA"
- Where the text mentions age of a person, the age should be replaced by "CENZURA".
There can't be two CENZURA words one after another, like "CENZURA CENZURA" - in such case it should be just one "CENZURA" word.
For example, such original text:
Znaleźliśmy, gdzie się ukrywa Adrian Miałczyński. Jego ostatnia znana lokalizacja to ulica Bulwarowa 7. W chwili obecnej ma 38 lat.
Should be corrected to:
Znaleźliśmy, gdzie się ukrywa CENZURA. Jego ostatnia znana lokalizacja to ulica CENZURA. W chwili obecnej ma CENZURA lat.
Please, respond only with the corrected text. It should be included in JSON format with key name "tekst".
The original text is as follows:
---
"""
prompt = prompt + input_text
model = "llama3.2"
json_to_ollama = {
    "model": model,
    "prompt": prompt,
    "stream": False,
    "format": "json",
    "temperature": 0
}
endpoint = f"http://{local_ollama_server}/api/generate"
output_raw = requests.post(endpoint, json=json_to_ollama)
output_text = output_raw.content.decode('utf-8')
output = json.loads(output_text)
response_text = output['response']
response = json.loads(response_text)
print ("The whole response is:")
pp (response, indent=4)
tekst = response['tekst']
print ("The output text is:")
print (tekst)
# Send the result to Central
task_response = send_task_response(aidevs_api_key, "CENZURA", tekst, f"https://centrala.{central_domain}/report")
pp (task_response)
