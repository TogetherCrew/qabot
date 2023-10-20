import requests

# r = requests.get("http://localhost:8000/")
#
# print(f"Result {r.text}")

list_to_search = ['Amin','Felipe','Ene','Neo4j']

for i in range(0, 500):
    search = list_to_search[i % 4]
    r = requests.get(f"http://localhost:1234/search/0/{search}")
    print(f"Search word:{search} result:: {r.text}")