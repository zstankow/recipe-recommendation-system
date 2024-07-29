from openai import OpenAI
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import json
import time
import os

load_dotenv()

ELASTIC_URL = os.getenv('ELASTIC_URL')
OLLAMA_URL = os.getenv('OLLAMA_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')


es_client = Elasticsearch(ELASTIC_URL) 
openai_client = OpenAI(api_key=OPENAI_API_KEY)
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
model = SentenceTransformer(MODEL_NAME)


def elastic_search_text(query, index_name="recipes"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["ingredients", "steps", "name", "description", "tags"],
                        "type": "best_fields",
                    }
                }
            }
        },
    }

    res = es_client.search(index=index_name, body=search_query)
    result_docs = []
    for hit in res["hits"]["hits"]:
        result_docs.append(hit['_source'])
    
    return result_docs


def elastic_search_knn(vector, field="text_vector", index_name="recipes"):
    knn = {
        "field": field,
        "query_vector": vector,
        "k": 5,
        "num_candidates": 10000,
    }

    search_query = {
        "knn": knn,
        "_source": ["ingredients", "steps", "name", "description", "tags"]
    }

    res = es_client.search(index=index_name, body=search_query)
    result_docs = []
    for hit in res["hits"]["hits"]:
        result_docs.append(hit['_source'])
    
    return result_docs


def build_prompt(query, search_results):
    prompt_template = """
You are a recipe creator assistant. Answer the QUERY based on the CONTEXT from the FAQ database.
Use only the recipes from the CONTEXT when answering the QUERY. Provide the recipe and the steps.
You do not need to use all the ingredients listed in the query if you don't recommend it. 

QUERY: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    
    for doc in search_results:
        context += f"Recipe title: {doc['name']}\ndescription: {doc['description']}\ningredients: {doc['ingredients']}\nsteps: {doc['steps']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt, model_choice):
    start_time = time.time()
    if model_choice.startswith('ollama/'):
        response = ollama_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    elif model_choice.startswith('openai/'):
        response = openai_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")
        
    end_time = time.time()
    response_time = end_time - start_time
    
    return answer, tokens, response_time


def evaluate_relevance(question, answer):
    prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer to the given question.
    Based on the relevance of the generated answer, you will classify it
    as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()

    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, 'openai/gpt-4o-mini')
    
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens
    
def calculate_openai_cost(model_choice, tokens):
    openai_cost = 0

    if model_choice == 'openai/gpt-3.5-turbo':
        openai_cost = (tokens['prompt_tokens'] * 0.0015 + tokens['completion_tokens'] * 0.002) / 1000
    elif model_choice in ['openai/gpt-4o', 'openai/gpt-4o-mini']:
        openai_cost = (tokens['prompt_tokens'] * 0.03 + tokens['completion_tokens'] * 0.06) / 1000

    return openai_cost

def get_answer(query, model_choice, search_type):
    if search_type == 'Vector':
        vector = model.encode(query)
        search_results = elastic_search_knn(field='text_vector', vector=vector)
    else:
        search_results = elastic_search_text(query)

    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model_choice)
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)
    openai_cost = calculate_openai_cost(model_choice, tokens)

    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': openai_cost
    }
