"""
Solution to task 12
- Unzip the downloaded data (pass: 1670)
- Index all files in vector base (Qdrant)
- Find the answer to the question (should be the first returned vector)
"""

import os
import re
from pprint import pp
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from lib.aidevs import send_task_response
from sekrety import aidevs_api_key, central_domain, openai_api_key, qdrant_api_key, qdrant_host
from lib.myai import MyAI

ai = MyAI(openai_api_key, False, 10)
task = "wektory"
directory = "downloads/weapons_tests/do-not-share"

qdrant = QdrantClient(host=qdrant_host, port=6333, api_key = qdrant_api_key)
# We prepare collection for size 1536 = text-embedding-3-small
if not qdrant.collection_exists("ai-devs"):
   qdrant.create_collection(
      collection_name="ai-devs",
      vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
   )

files = os.listdir(directory)
data = {}
index = 0
for filename in files:
    index += 1
    with open (os.path.join(directory, filename), 'r', encoding='utf-8') as file:
        data[filename] = file.read()
        embedding = ai.embedding(data[filename], source="Embedding")
        qdrant.upsert(
            collection_name="ai-devs",
            points=[
                PointStruct(
                    id=index,
                    vector=embedding,
                    payload={"filename": filename}
                )
            ]
        )
search_text = "W raporcie z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
search_embedding = ai.embedding(search_text, source="Search embedding")
search_result = qdrant.search(
    collection_name="ai-devs",
    query_vector=search_embedding,
    limit=1
)
found_filename = search_result[0].payload['filename']
print (f"Found filename: {found_filename}")
filename_fields = re.findall("(\d\d\d\d)_(\d\d)_(\d\d)\.txt", found_filename)
answer = f"{filename_fields[0][0]}-{filename_fields[0][1]}-{filename_fields[0][2]}"
print (f"Response date: {answer}")
task_response = send_task_response(aidevs_api_key, task, answer, f"https://centrala.{central_domain}/report")
print ("\n\nFINAL TASK RESPONSE:")
pp (task_response, indent=4)
