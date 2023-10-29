import time

import requests

# r = requests.post('http://localhost:3333/dev_token')
# token = r.json()['access_token']
# print(token)


r = requests.post("http://localhost:3333/ask", json={
    'question': 'What Neo4j is used for?'
},
    #               , headers={
    # 'Authorization': f'Bearer {token}'},
                  stream=True)

start = time.time()
r.raise_for_status()
for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
    print(f"Got result {round(time.time() - start, 1)}s after start: '{chunk}'")