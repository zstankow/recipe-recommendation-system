import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from tqdm.auto import tqdm
from dotenv import load_dotenv
from db import init_db
import os
load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")
MODEL_NAME = os.getenv("MODEL_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")

def fetch_documents():
    print('Fetching documents...')
    with open('recipes.json', 'r') as json_file:
        documents = json.load(json_file)
    return documents

def index_documents(es_client, documents, model):
    print('Indexing documents...')
    operations = []
    for doc in documents:
        operations.append(doc)

    for doc in tqdm(operations, total=len(operations)):
        es_client.index(index=INDEX_NAME, document=doc)
    print(f"Indexed {len(documents)} documents")


def load_model():
    print(f"Loading model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

# def fetch_ground_truth():
#     print("Fetching ground truth data...")
#     relative_url = "03-vector-search/eval/ground-truth-data.csv"
#     ground_truth_url = f"{BASE_URL}/{relative_url}?raw=1"
#     df_ground_truth = pd.read_csv(ground_truth_url)
#     df_ground_truth = df_ground_truth[
#         df_ground_truth.course == "machine-learning-zoomcamp"
#     ]
#     ground_truth = df_ground_truth.to_dict(orient="records")
#     print(f"Fetched {len(ground_truth)} ground truth records")
#     return ground_truth


def setup_elasticsearch():
    print("Setting up Elasticsearch...")
    es_client = Elasticsearch("http://localhost:9200")

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

    es_client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
    es_client.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Elasticsearch index '{INDEX_NAME}' created")
    return es_client

def main():
    print("Starting the indexing process...")
    documents = fetch_documents()
    # ground_truth = fetch_ground_truth()
    es_client = setup_elasticsearch()
    model = load_model()
    index_documents(es_client, documents, model)

    print("Initializing database...")
    init_db()

    print("Indexing process completed successfully!")

if __name__ == "__main__":
    main()
