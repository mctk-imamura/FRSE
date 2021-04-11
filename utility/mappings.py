# -*- coding: utf-8 -*-
import elasticsearch

mapping = {
    "mappings" : {
        "properties" : {
            "number": {"type":"long"},
            "title": {
                "type":"text",
                "analyzer": "kuromoji",
                "fields": {
                    "keyword": {"type": "keyword",
                    "ignore_above": 100000
                    }
                }
            },
            "country": {"type":"text"},
            "organization": {"type":"text"},
            "source": {"type":"text"},
            "path": {"type":"text"},
            "content": {
                "type":"text",
                "analyzer": "kuromoji",
                "fields": {
                    "keyword": {"type": "keyword",
                    "ignore_above": 100000
                    }
                }
            },
            "content_k": {
                "type":"keyword",
            }
        }
    }
}
client = elasticsearch.Elasticsearch("localhost:9200")
try:
    client.indices.delete(index='fuel_research')
except:
    pass
client.indices.create(index='fuel_research', body=mapping)