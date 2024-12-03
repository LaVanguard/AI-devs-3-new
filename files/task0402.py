"""
Solution to task 17 - train the model, and then verify the samples
- Get the zip file
- Collect the lists of samples (correct and incorrect)
- Prepare the jsonl file (trainfile.jsonl)
- (file to be manually fed to OpenAI to train a gpt-4o-mini model)
- after training the model on OpenAI platform - get the model name, and replace the gpt-4o-mini one
- validate the samples with new model
- send the list of correct samples to HQ
"""

import zipfile
import os
import requests
import json
from pprint import pp
from lib.aidevs import send_task_response
from sekrety import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

source_url = f"https://centrala.{central_domain}/dane/lab_data.zip"
model = "gpt-4o-mini"
ai = MyAI(openai_api_key, False, 15)
task = "research"

def download_and_extract_zip(url, download_dir='downloads', zip_filename='downloaded_zipfile.zip', extract_dir='extracted'):
    # Create download subdirectory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    # Download the file
    local_zip_path = os.path.join(download_dir, zip_filename)
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_zip_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded ZIP file to {local_zip_path}")
    else:
        print("Failed to download the file.")
        return
    # Create extraction subdirectory if it doesn't exist
    full_extract_dir = os.path.join(download_dir, extract_dir)
    if not os.path.exists(full_extract_dir):
        os.makedirs(full_extract_dir)
    # Extract the ZIP file
    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(full_extract_dir)
        print(f"Extracted files to {full_extract_dir}")
    # List all extracted files
    extracted_files = os.listdir(full_extract_dir)
    print("Extracted files:")
    pp(extracted_files, indent=4)
    return full_extract_dir

directory = download_and_extract_zip(source_url, "downloads", "lab_data.zip", "lab_data")
correct = []
incorrect = []
verify = {}
with open (os.path.join(directory, "correct.txt"), 'r') as file:
    for line in file:
        if len(line)>2:
            correct.append(line.strip())
with open (os.path.join(directory, "incorrect.txt"), 'r') as file:
    for line in file:
        if len(line)>2:
            incorrect.append(line.strip())
with open (os.path.join(directory, "verify.txt"), 'r') as file:
    for line in file:
        if len(line)>2:
            elements = line.strip().split("=")
            verify[elements[0]] = elements[1]

# Now we prepare the training file
with open ("trainfile.jsonl", 'w+') as file:
    for line in correct:
        object = {
            "messages": [
                {"role": "system", "content": "Verify the samples validity"},
                {"role": "user", "content": line},
                {"role": "assistant", "content": "correct"}
            ]
        }
        file.write(json.dumps(object))
        file.write("\n")
    for line in incorrect:
        object = {
            "messages": [
                {"role": "system", "content": "Verify the samples validity"},
                {"role": "user", "content": line},
                {"role": "assistant", "content": "incorrect"}
            ]
        }
        file.write(json.dumps(object))
        file.write("\n")

# Preparing the response
correct_list = []
for entry in verify:
    messages=[
        {"role": "system", "content": "Verify the samples validity"},
        {"role": "user", "content": verify[entry]}
    ]
    response = ai.chat_completion(messages, model, 10, 0, "validation")
    pp (messages, indent=4, width=200)
    print (response)
    if response == "correct":
        correct_list.append(entry)

pp (correct_list, indent=4, width=200)

response = send_task_response(aidevs_api_key, task, correct_list, f"https://centrala.{central_domain}/report")
print ("\n\nResponse from HQ:")
pp (response)
