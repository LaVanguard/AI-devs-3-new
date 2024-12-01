from pprint import pp

from lib.aidevs import send_task_response
from sekrety import aidevs_api_key, central_domain

task = "webhook"
answer = "https://azyl-50452.ag3nts.org/"
task_response = send_task_response(aidevs_api_key, task, answer, f"https://centrala.{central_domain}/report")
print ("\n\nFINAL TASK RESPONSE:")
pp (task_response, indent=4)
print (79*"=")
