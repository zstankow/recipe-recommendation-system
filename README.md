# RAG Recipe Assistant

## Overview
The RAG Recipe Assistant is an advanced RAG application designed to help you find the perfect recipes based on your preferences and available ingredients. Leveraging the power of ElasticSearch for both text and vector searches, and integrating advanced methods such as Sentence Transformer, Ollama and Phi3 from HuggingFace, and various OpenAI models (GPT-4o, GPT-3.5-turbo, GPT-4o-mini), this assistant provides accurate and relevant recipe suggestions. 


## Key Features:
- Model Selection: __Choose from multiple language models__ including OpenAI's GPT (GPT-4o, GPT-3.5-turbo, GPT-4o-mini) or HuggingFace models (phi3) via Ollama.
- Search Types: Utilize either __text-based or vector-based__ search for retrieving recipe data.
- User-Friendly Input: Enter your culinary queries and receive tailored recipe suggestions.
- Real-Time Feedback: Rate the relevance of the answers with easy-to-use __feedback buttons__.
- Conversation History: View recent interactions and filter them based on relevance.
- Detailed Analytics: __Track detailed metrics__ including response time, relevance, model used, token count, and cost per query.
- Response Evaluation: Utilizes __LLM-as-a-judge__ method to determine if response was relevant, partially relevant, or not relevant to query.
- Database Integration: Conversations, feedback, and analytics are stored in a __PostgreSQL database__ for comprehensive data management.
- Live Data Visualization: Monitor live data and feedback trends through an integrated __Grafana dashboard__

--------------------------------------------------------------------------------------------------------------------------------------

# Grafana Dashboard
![image](https://github.com/user-attachments/assets/a8cdc02e-c5e5-402d-9c32-6cc363c8f215)
![image](https://github.com/user-attachments/assets/c541d082-aa7a-4793-882a-94a285fb2e34)

--------------------------------------------------------------------------------------------------------------------------------------

# Streamlit App UI
![alt text](image.png)

--------------------------------------------------------------------------------------------------------------------------------------

# Example input/output:

![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)

--------------------------------------------------------------------------------------------------------------------------------------

## Installation

1. Clone the repository
```bashrc
git clone https://github.com/zstankow/ollama-FAQ-assistant.git
```
2. Navigate to the directory
```bashrc
cd recipe-recommendation-system/app
```
3. Download the dataset
```bashrc
curl -L -o recipes.json https://github.com/zstankow/recipe-recommendation-system/releases/download/recipes/recipes.json
```

4. Build and run the Docker containers
```bashrc
docker-compose build streamlit
docker-compose up
```

5. In a separate terminal navigate to the directory and run
`python prep.py`
This will initialize the postgres database.

6. To use the phi3 model, navigate to directory in a new bash terminal
```bashrc
docker exec -it ollama bash
```
```bashrc
ollama pull phi3
```

This downloads the phi3 model if you choose to use ollama with CPU instead of outsourcing to an OpenAI model. 

7. To open the app, paste in url `http://localhost:8501/`


