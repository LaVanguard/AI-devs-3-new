"""
Let's check all possible DB entries one by one :)
"""

import requests
import re
from time import sleep
from pprint import pp

from lib.aidevs import send_task_response, get_response
from secrets import aidevs_api_key, central_domain, openai_api_key

print (79*"=")
people_api = f"https://centrala.{central_domain}/people"
places_api = f"https://centrala.{central_domain}/places"

people_counter = 0
places_counter = 0
people = ['BARBARA','ALEKSANDER','RAFAL','ANDRZEJ']
places = ['KRAKOW','WARSZAWA']
loop = True
while loop:
    sleep(1)
    if len(people) > people_counter:
        answer = get_response(aidevs_api_key, "", people[people_counter], people_api)
        if answer['code']==0:
            print (f"{people[people_counter]} -> {answer['message']}")
            newlist = re.findall("([A-Z]+)", answer['message'])
            for place in newlist:
                if place not in places:
                    places.append(place)
        else:
            print (f"{people[people_counter]} !! code {answer['code']}, {answer['message']}")
        people_counter += 1
    elif len(places) > places_counter:
        answer = get_response(aidevs_api_key, "", places[places_counter], places_api)
        if answer['code']==0:
            print (f"{places[places_counter]} -> {answer['message']}")
            newlist = re.findall("([A-Z]+)", answer['message'])
            for person in newlist:
                if person not in people:
                    people.append(person)
        else:
            print (f"{places[places_counter]} !! code {answer['code']}, {answer['message']}")
        places_counter += 1
    else:
        loop=False
pp (people, indent=4)
pp (places, indent=4)