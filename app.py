import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

api_key =load_dotenv('OPENAI_API_KEY')
client = OpenAI(api_key='api_key')

es_client = Elasticsearch('http://localhost:9200') 

model_name = 'multi-qa-MiniLM-L6-cos-v1'
model = SentenceTransformer(model_name)
index_name = "recipes"

def elastic_search(search_term):
    vector_search_term = model.encode(search_term)
    search_query = {
        "field": "text_vector",
        "query_vector": vector_search_term,
        "k": 5,
        "num_candidates": 10000,
    }

    res = es_client.search(index=index_name, knn=search_query, source=["ingredients", "steps", "name", "description", "tags"])
    result_docs = []
    for hit in res["hits"]["hits"]:
        result_docs.append(hit['_source'])

    return result_docs

def build_prompt(q, search_results):
    prompt_template = """
You are a recipe creator assistant. Answer the QUERY based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUERY.

QUERY: {query}

CONTEXT: 
{context}
""".strip()

    context = ""
    
    for doc in search_results:
        context += f"Recipe title: {doc['name']}\ndescription: {doc['description']}\ningredients: {doc['ingredients']}\nsteps: {doc['steps']}\n\n"
    
    prompt = prompt_template.format(query=q, context=context).strip()
    return prompt

def llm(prompt):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag(q):
    res = elastic_search(q)
    prompt = build_prompt(q, res)
    answer = llm(prompt)
    return answer

def main():
    st.title("RAG Recipe Assistant")

    user_input = st.text_input("Enter your query. (Hint: What do you feel like eating? What ingredients do you have? How much time do you have?)")
    if st.button("Ask"):
        with st.spinner('Processing...'):
            output = rag(user_input)
            st.success("Completed!")
            st.write(output)

if __name__ == "__main__":
    main()