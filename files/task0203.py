"""
Solution to 8th task.
- Get the witness description of the robot
- Generate image of the robot
- Send the image URL to Central
"""
import requests
import json
from pprint import pp

from lib.aidevs import send_task_response
from secrets import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

model = "dall-e-3"
ai = MyAI(openai_api_key, False, 2)
# Open the task source page and get the data to anonimize
input_link = f"https://centrala.{central_domain}/data/{aidevs_api_key}/robotid.json"
print (f"\nOtwieram strone: {input_link}")
input_raw = requests.get(input_link)             # The data is still in binary format
input = input_raw.json()
prompt = """
Based on the below description from the eye-witness, please list all information we have about the robot's appearance. Then please draw a picture of the described robot:
---
"""
prompt = prompt + input['description']
result = ai.images_generate(prompt, model)
pp (result, indent=4)
image_url = result.data[0].url
print (f"\nThe URL is: {image_url}")
response = send_task_response(aidevs_api_key, "robotid", image_url, f"https://centrala.{central_domain}/report")
pp (response, indent=4)
