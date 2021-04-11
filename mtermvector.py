import requests
import json
body = {
  "ids": [ "1", "2" ],
  "parameters": {
    "fields": [
      "content"
    ]
  }
}

request = requests.post("http://localhost:9200/fuel_research/_mtermvectors/", json = body)
result = request.json()

print(result['docs'][0]['term_vectors'])

