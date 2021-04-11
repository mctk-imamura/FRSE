import requests
from elasticsearch import Elasticsearch
import csv

es = Elasticsearch()
body = {
    "query" : {
        "match_all": {}
    }
}

result = es.search(index='fuel_research', body=body, size=10000)
ids = [result['hits']['hits'][i]['_id'] for i  in range(result['hits']['total']['value'])]
#print(ids)

params = {
            "fields" : "content",
            "field_statistics" : "false",
            "offsets" : "false",
            "positions" : "false"
        }

terms = {}

for n in ids:
	request = requests.get("http://localhost:9200/fuel_research/_termvectors/" + n, params = params)
	result = request.json()

	d = result["term_vectors"]["content"]["terms"]

	for k, v in d.items():
		if k in terms:
			terms[k] += v['term_freq']
		else:
			terms[k] = v['term_freq']

#print(terms)

with open("test.csv",'w', newline="") as f:
	writer = csv.writer(f, delimiter=",",quotechar='"')

	for k, v in terms.items():
		writer.writerow([k,v])
