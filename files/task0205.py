"""
Solution to 10th task
- download the webpage with the paper
- download the HQ questions
- scrape? - to have paper text + image descriptions in one piece
- answer the questions with the scraped paper in context
- return the answers to HQ
"""

import requests
import json
import os
import zipfile
import re
import base64
import sys
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from pprint import pp

from lib.aidevs import send_task_response
from secrets import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

ai = MyAI(openai_api_key, False, 10)
model = "gpt-4o-mini"
page_dir = f"https://centrala.{central_domain}/dane/"
page = page_dir + "arxiv-draft.html"
try:
    page_raw = requests.get(page)
except Exception as error:
    print (f"Error in GET request: {error}")
    sys.exit(1)
page_text = page_raw.content.decode('utf8')   # Decode from binary to ASCII, still one string
page_nice = md(page_text)
soup = BeautifulSoup(page_raw.content, "html.parser")
result = soup.find("div", class_="container")
page_text = """
    <h2>Analiza incydentu: wpływ dodatkowego obiektu na transmisję</h2>
    <p>Podczas szczegółowej analizy incydentu z udziałem Rafała Bomby zespół badawczy odkrył kluczowy element, który najprawdopodobniej przyczynił się do niepowodzenia transmisji. Mimo że parametry wejściowe i wyjściowe transmitera były poprawnie ustawione, obecność dodatkowego przedmiotu wniesionego do komory temporalnej mogła istotnie zakłócić cały proces. </p> 
    <p>Wniesiony przez Bombę przedmiot niemal na pewno spowodował niepożądane połączenie obu elementów podczas przesyłu, co mogło doprowadzić do drastycznej ingerencji w strukturę jego DNA, a nawet do śmiertelnych uszkodzeń. Badacze są zgodni co do tego, że najprawdopodobniejdoszło do fuzji cząsteczek obu obiektów. </p> 
    <p>Fuzja na poziomie komórkowym to zjawisko, którego skutki trudno przewidzieć, ale w tym przypadku oznaczałaby mutacje na skalę całego organizmu, co  w skrajnych przypadkachmoże być jednoznaczne ze śmiercią.</p>
    <p> Przeprowadzone symulacje wskazują, że takie zakłócenia mogły wywołać nieodwracalne zmiany strukturalne, które – w najłagodniejszym scenariuszu – prowadzą do głębokich deformacji ciała lub niekontrolowanej reakcji genetycznej. </p> 
    <p>Na miejscu zdarzenia znaleziono dyktafon z jednym plikiem dźwiękowym. Nie wiemy dlaczego Bomba przygotowywał nagranie i kto miał być jego odbiorcą.</p>
    <audio controls>
        <source src="i/rafal_dyktafon.mp3" type="audio/mpeg">
        Twoja przeglądarka nie obsługuje elementu audio.
    </audio>
    <p><a href="i/rafal_dyktafon.mp3" download>rafal_dyktafon.mp3</a></p>

    <p>Istniała realna obawa, że incydent ten zakończył się śmiercią Bomby lub że w najlepszym razie przemieścił się on w czasie w formie organizmu, który nie przypomina już swojego pierwowzoru. Incydent ten stanowi ostrzeżenie dla zespołu badawczego i podkreśla potrzebę ścisłej kontroli nad procesem transmisji temporalnej oraz wyeliminowania ryzyka przypadkowej fuzji obiektów. </p> 

    <h2>Podniesienie poziomu bezpieczeństwa w laboratorium: nowe procedury i zabezpieczenia</h2>
"""
images = {}
audios = {}
for figure in result.find_all("figure"):
    image = figure.find("img")
    caption = figure.find("figcaption")
    images[image['src']] = {"caption": caption.get_text()}
for audio_entry in result.find_all("audio"):
    audio = audio_entry.find("source")
    audios[audio['src']] = {}
for image in images:
    image_file = requests.get(page_dir + image)
    with open("downloads/tempfile.png", "wb") as f:
        f.write(image_file.content)
        f.close()
    image64 = encode_image("downloads/tempfile.png")
    prompt = f"""
    The attached image is a part of a pseudo-scientific paper.
    Please interpret it with the given context. The image was put in the text with following caption:
    <caption>
    {images[image]['caption']}
    </caption>
    Your task is to describe in few sentences what you see in the image.
    Please try to describe the overall image meaning and situation, and also describe the contents and details of the image.
    Where could the picture be taken?
    What are the main elements of the picture?
    What else can you say about the image?
    Please write everything in one line, without any line breaks.
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": [{
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image64}"
            }
        }]
        }
    ]
    answer = ai.chat_completion(messages, model, 500, 0)
    images[image]['description'] = answer
    page_nice = re.sub(f"!\[\]\({image}\)", f"(Here in the paper was an image:\n<image_description>\n{answer}\n</image_description>\n)", page_nice)
for audio in audios:
    audio_download = requests.get(page_dir + audio)
    with open("downloads/tempfile.mp3", "wb") as f:
        f.write(audio_download.content)
        f.close()
    with open("downloads/tempfile.mp3", "rb") as audio_file:
        audio_text = ai.transcribe(audio_file)
    audios[audio]['text'] = audio_text
    page_nice = re.sub("Twoja przeglądarka nie obsługuje elementu audio.", "", page_nice)
    page_nice = re.sub(f"\[.*?\]\({audio}\)", f"(Here in the paper was an audio recording. Below is the transcription:\n<audio_transcription>\n{audio_text}\n</audio_transcription>\n)", page_nice)

print (page_nice)
