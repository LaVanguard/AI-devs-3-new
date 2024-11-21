"""
Solution to 14th task:
- Build prompt for AI to send names or places to check in Central API, in a loop building a bigger context, or - if confident - send answer.
- Based on the decision - run next query in database, or return answer.
- OFC - report answer to Central and get the flag :)
"""

import requests
import re
from pprint import pp

from lib.aidevs import send_task_response, get_response
from secrets import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

# Downloaded script to remove Polish characters
def remove_accents(input_text):
    strange='ŮôῡΒძěἊἦëĐᾇόἶἧзвŅῑἼźἓŉἐÿἈΌἢὶЁϋυŕŽŎŃğûλВὦėἜŤŨîᾪĝžἙâᾣÚκὔჯᾏᾢĠфĞὝŲŊŁČῐЙῤŌὭŏყἀхῦЧĎὍОуνἱῺèᾒῘᾘὨШūლἚύсÁóĒἍŷöὄЗὤἥბĔõὅῥŋБщἝξĢюᾫაπჟῸდΓÕűřἅгἰშΨńģὌΥÒᾬÏἴქὀῖὣᾙῶŠὟὁἵÖἕΕῨčᾈķЭτἻůᾕἫжΩᾶŇᾁἣჩαἄἹΖеУŹἃἠᾞåᾄГΠКíōĪὮϊὂᾱიżŦИὙἮὖÛĮἳφᾖἋΎΰῩŚἷРῈĲἁéὃσňİΙῠΚĸὛΪᾝᾯψÄᾭêὠÀღЫĩĈμΆᾌἨÑἑïოĵÃŒŸζჭᾼőΣŻçųøΤΑËņĭῙŘАдὗპŰἤცᾓήἯΐÎეὊὼΘЖᾜὢĚἩħĂыῳὧďТΗἺĬὰὡὬὫÇЩᾧñῢĻᾅÆßшδòÂчῌᾃΉᾑΦÍīМƒÜἒĴἿťᾴĶÊΊȘῃΟúχΔὋŴćŔῴῆЦЮΝΛῪŢὯнῬũãáἽĕᾗნᾳἆᾥйᾡὒსᾎĆрĀüСὕÅýფᾺῲšŵкἎἇὑЛვёἂΏθĘэᾋΧĉᾐĤὐὴιăąäὺÈФĺῇἘſგŜæῼῄĊἏØÉПяწДĿᾮἭĜХῂᾦωთĦлðὩზკίᾂᾆἪпἸиᾠώᾀŪāоÙἉἾρаđἌΞļÔβĖÝᾔĨНŀęᾤÓцЕĽŞὈÞუтΈέıàᾍἛśìŶŬȚĳῧῊᾟάεŖᾨᾉςΡმᾊᾸįᾚὥηᾛġÐὓłγľмþᾹἲἔбċῗჰხοἬŗŐἡὲῷῚΫŭᾩὸùᾷĹēრЯĄὉὪῒᾲΜᾰÌœĥტ'
    ascii_replacements='UoyBdeAieDaoiiZVNiIzeneyAOiiEyyrZONgulVoeETUiOgzEaoUkyjAoGFGYUNLCiIrOOoqaKyCDOOUniOeiIIOSulEySAoEAyooZoibEoornBSEkGYOapzOdGOuraGisPngOYOOIikoioIoSYoiOeEYcAkEtIuiIZOaNaicaaIZEUZaiIaaGPKioIOioaizTIYIyUIifiAYyYSiREIaeosnIIyKkYIIOpAOeoAgYiCmAAINeiojAOYzcAoSZcuoTAEniIRADypUitiiIiIeOoTZIoEIhAYoodTIIIaoOOCSonyKaAsSdoACIaIiFIiMfUeJItaKEISiOuxDOWcRoiTYNLYTONRuaaIeinaaoIoysACRAuSyAypAoswKAayLvEaOtEEAXciHyiiaaayEFliEsgSaOiCAOEPYtDKOIGKiootHLdOzkiaaIPIIooaUaOUAIrAdAKlObEYiINleoOTEKSOTuTEeiaAEsiYUTiyIIaeROAsRmAAiIoiIgDylglMtAieBcihkoIrOieoIYuOouaKerYAOOiaMaIoht'
    translator=str.maketrans(strange,ascii_replacements)    
    return input_text.translate(translator)

print (79*"=")
ai = MyAI(openai_api_key, False, 10)
model = "gpt-4o-mini"
task = "loop"
people_api = f"https://centrala.{central_domain}/people"
places_api = f"https://centrala.{central_domain}/places"
initial_page = f"https://centrala.{central_domain}/dane/barbara.txt"
# Get the initial information from the given page
try:
    page_raw = requests.get(initial_page)
except Exception as error:
    print (f"Error in GET request: {error}")
    sys.exit(1)
page_text = page_raw.content.decode('utf8')   # Decode from binary to ASCII, still one string
# Build the initial prompt
system_prompt = """
You are **investigator** bot. Your task is to find the place (city name) where Barbara Zawadzka is staying.
You have access to a database where information about different people and different cities are held. They will give you information about other related people and cities. You need to analyze the relationships.
At each step, analyze all collected information, think if you already know the place where Barbara Zawadzka is, or analyze which cities or people that you haven't checked yet, you would like to check.
At each step, you can either decide that you are ready to answer the question (where is Barbara Zawadzka?) or that you want to check specific person or place information. You can explain your reasoning.
- If you would like to check the database info about a city, end the sentence with last line "CITY = " followed by the city name, for example if you want to check Kołobrzeg, it will be: "CITY = Kołobrzeg".
- If you would like to check the database info about a person, end the sentence with last line "PERSON = " followed by the person's first name in its base form in Polish language (w mianowniku), for example is your trace is "widziano z nią Bogumiła" and you want to check this person, you end with "PERSON = Bogumił".
- If you know the city where Barbara Zawadzka is, end with "ANSWER = " followed by the city name you found. For example "ANSWER = SZCZECIN".
Please, do not check the same city or person in the database more then once. Please also don't give the same answer more than once, if you already got information the answer was not correct.
Good luck!
"""
message_prompt = """
## This is the initial information we have:
"""
message_prompt += page_text
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": message_prompt}
]
print (f"{message_prompt}\n\n\n")
# Run the queries in loop until the city is found
loop = True
while loop:
    ai_answer = ai.chat_completion(messages, model, 500, 0)
    print (f"{ai_answer}\n\n\n")
    messages.append({"role": "assistant", "content": ai_answer})
    message = ""
    city = re.findall("CITY = (.*?)\s*$",ai_answer)
    person = re.findall("PERSON = (.*?)\s*$",ai_answer)
    answer = re.findall("ANSWER = (.*?)\s*$",ai_answer)
    if city:
        api_answer = get_response(aidevs_api_key, "", remove_accents(city[0]).upper(), places_api)
        city_info = api_answer['message']
        message = f"## The database response for city: {city[0]}\n\n{city_info}"
    if person:
        api_answer = get_response(aidevs_api_key, "", remove_accents(person[0]).upper(), people_api)
        person_info = api_answer['message']
        message = f"## The database response for person: {person[0]}\n\n{person_info}"
    if answer:
        final_answer = answer[0]
        task_response = send_task_response(aidevs_api_key, task, remove_accents(final_answer).upper(), f"https://centrala.{central_domain}/report")
        pp (task_response, indent=4)
        if task_response['code'] != 0:
            message = f"## Sorry, the answer is NOT correct. Barbara is not in {final_answer}. Please, keep looking!"
        else:
            loop = False
    print (f"{message}\n\n\n")
    messages.append({"role": "user", "content": message})
pp (task_response, indent=4)