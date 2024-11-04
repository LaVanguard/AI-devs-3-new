"""
Simple solution to first task.
- open webpage (xyz)
- read "captcha" question
- send request as POST
- get the webpage
"""

import requests
import re
import sys
from openai import OpenAI

from lib.usedtokens import UsedTokens
from secrets import openai_api_key, central_domain

page = f"https://xyz.{central_domain}"
username = "tester"
password = "574e112a"

tokens = UsedTokens(False)      # Start counting tokens you use!
openai = OpenAI(api_key = openai_api_key)   # Prepare openai object before timer starts ticking
try:
    page_raw = requests.get(page)
except Exception as error:
    print (f"Error in GET request: {error}")
    sys.exit(1)
page_text = page_raw.content.decode('utf8')   # Decode from binary to ASCII, still one string
question = re.findall('<p id="human-question">Question:<br />(.*?)</p>',page_text)
if not question:
    print ("Nie znaleziono pytania na stronie! Poniżej zrzut strony:\n")
    print(page_text)
    sys.exit(1)
print (f"Pytanie to: {question[0]}")
messages = [
    { "role": "system", "content": "Twoim zadaniem jest odpowiedzieć na pytanie zadane przez użytkownika. Odpowiedź powinna być tak krótka, jak to możliwe, i zawierać tylko jedną liczbę która odpowiada na pytanie."},
    { "role": "user", "content": question[0] }
]
model = "gpt-4o"
try:
    chat_completion = openai.chat.completions.create(
        messages = messages,
        model = model,
        max_tokens = 10,
        temperature = 0
    )
    tokens.log(chat_completion)
    answer = chat_completion.choices[0].message.content
    answer = int(answer.strip()) if answer.strip().isdecimal() else 1
except Exception as error:
    print (f"Error in OpenAI completion: {error}")
    sys.exit(1)
print (f"Answer: {answer}")
form_values = {
    "username": username,
    "password": password,
    "answer": answer
}
try:
    result_raw = requests.post(page, data=form_values)
except Exception as error:
    print (f"Error sending the answer: {error}")
    sys.exit(1)
result_text = result_raw.content.decode('utf8')
print ("\nThe result page is:\n")
print (result_text)
flag = re.findall('{{FLG:(.*?)}}', result_text)
if flag:
    print (f"\n\nZnaleziono flagę: {flag[0]}")
