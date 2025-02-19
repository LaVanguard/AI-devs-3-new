import requests
import json
import sys
import re
from pprint import pp
from markdownify import markdownify as md
from sekrety import openai_api_key, pushover_user_key, pushover_api_key
from lib.myai import MyAI

ai = MyAI(openai_api_key, True, 20)
model = "gpt-4o"
pushover_url = "https://api.pushover.net/1/messages.json"

with open("checked_pages.json","r", encoding='utf-8') as file:
    checked_pages = json.load(file)
with open("pages_dump.json","r", encoding='utf-8') as file:
    pages_dump = json.load(file)
was_dump_changed = False

for page in checked_pages:
    try:
        page_raw = requests.get(checked_pages[page]['link'])
    except Exception as error:
        print (f"Error in GET request: {error}")
        sys.exit(1)
    page_text = page_raw.content.decode('utf8')
    regex_result = re.findall(checked_pages[page]['regex'], page_text)
    if pages_dump[page]['regex_value'] == "":
        print (f"Page '{page}' loaded for the first time - saving.")
        page_nice = md(page_text)
        pages_dump[page]['regex_value'] = regex_result[0]
        pages_dump[page]['markdown_text'] = page_nice
        was_dump_changed = True
    else:
        print (f"Page '{page}' loaded from JSON.")
    if pages_dump[page]['regex_value'] == regex_result[0]:
        print (f"Page '{page}' was not updated.")
    else:
        print (f"Page '{page}' WAS UPDATED! Running automation.")
        old_page = pages_dump[page]['markdown_text']
        new_page = md(page_text)
        messages = [
            {"role": "system", "content": 'Pomóż użytkownikowi znaleźć różnice pomiędzy starą wersją strony (oznaczoną jako "old_page") a nową wersją (oznaczoną jako "new_page"). Napisz w kilku (maksymalnie 5!) zdaniach, co zmieniło się na stronie.'},
            {"role": "user", "content": f"<old_page>\n{old_page}\n</old_page>\n\n---\n\n<new_page>\n{new_page}\n</new_page>"}
        ]
        result = ai.chat_completion(messages, model, max_tokens=300, temperature=0)
        print (f"Zmiany na stronie '{page}':\n{result}")
        pages_dump[page]['markdown_text'] = new_page
        pages_dump[page]['regex_value'] = regex_result[0]
        was_dump_changed=True
        r = requests.post(pushover_url, data = {
            "token": pushover_api_key,
            "user": pushover_user_key,
            "message": f"Zmiana strony {page}. {result}",
            "url": checked_pages[page]['link'],
            "url_title": page})

if was_dump_changed:
    with open("pages_dump.json","w", encoding='utf-8') as file:
        json.dump(pages_dump, file, ensure_ascii=False, indent=4)
        print ("Dump update was saved!")
else:
    print ("No updates to be saved.")
