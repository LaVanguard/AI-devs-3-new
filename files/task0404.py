"""
Solution to 19th task:
- Run the web server (Flask)
- Listen to POST request with {"instruction": "human text explaining the drone flight"}
- Return JSON with {"description": "two words"} - max 2 words describing what is in the map sector
- Test CURL example:
  curl -X POST -H "Content-Type: application/json" -d "{\"instruction\": \"Poleciałem w prawo\"}" https://azyl-50452.ag3nts.org/
"""

import sys
from pprint import pp
from flask import Flask, request, jsonify

from lib.aidevs import send_task_response, get_response
from sekrety import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

ai = MyAI(openai_api_key, True, 5)
model = "gpt-4o-mini"

app = Flask(__name__)

system_prompt = """
You are a remote navigator in a game, explaining the player what is in the sector of the game he entered (flied to).
The player starts the drone in the field marked as "start", and from that field he does series of movements, ending in other field.
Your task is to tell what is in the field the user ended on. Return just the word or two words that are written on the game map.
The game has 4 x 4 squares, and player starts in the top left field.
The game map is as follows:
---------------------------------------------------------------------------------
| start             | trawa             | trawa drzewo      | dom               |
---------------------------------------------------------------------------------
| trawa             | trawa wiatrak     | trawa             | trawa             |
---------------------------------------------------------------------------------
| trawa             | trawa             | skały             | trawa drzewa      |
---------------------------------------------------------------------------------
| skały             | skały             | samochód          | jama jaskinia     |
---------------------------------------------------------------------------------
Based on player explanation of where he flied from the "start" field, return the words that are inside his destination field.
Respond with just the word (or words), with nothing else.
"""

@app.route("/", methods=['POST'])
def webpage():
    content = request.json
    print (f"Received JSON:")
    pp (content, indent=4, width=200)
    user_prompt = content['instruction']
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = ai.chat_completion(messages, model, 10, 0)
    print (f"Response from AI: {response}")
    return jsonify({"description": response})

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=50452, debug=True)
