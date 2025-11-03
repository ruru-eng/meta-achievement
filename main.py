from secrets import client
from requests import request
import json

client_id = client.get("CLIENT_ID")
client_secret = client.get("CLIENT_SECRET")

url = "https://oauth.battle.net/token"

data = {
    "grant_type":"client_credentials"
}

response = request("POST",url,auth=(client_id,client_secret),data=data)

print(json.dumps(response.json(),indent=4))