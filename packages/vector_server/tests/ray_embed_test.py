import requests

# r = requests.get("http://localhost:8000/")
#
# print(f"Result {r.text}")

for i in range(0, 1000):
    r = requests.get("http://localhost:1234/update")

    print(f"Result update {r.text}")