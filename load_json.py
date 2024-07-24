import json
from elasticsearch import Elasticsearch
from tqdm import tqdm

es_client = Elasticsearch("http://localhost:9200")
index_name = "recipes"

index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "ingredients": {"type": "text"},
            "steps": {"type": "text"},
            "name": {"type": "text"},
            "description": {"type": "text"},
            "tags": {"type": "text"},
            "n_ingredients": {"type": "integer"},
            "n_steps": {"type": "integer"},
            "id": {"type": "keyword"},
            "text_vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            },
        }
    }
}

es_client.indices.delete(index=index_name, ignore_unavailable=True)
es_client.indices.create(index=index_name, body=index_settings)

with open('recipes.json', 'r') as json_file:
    documents = json.load(json_file)

operations = []
for doc in documents:
    operations.append(doc)

for doc in tqdm(operations, total=len(operations)):
    try:
        es_client.index(index=index_name, document=doc)
    except Exception as e:
        print(e)
