import time
import random
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from db import save_conversation, save_feedback
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
# Set the timezone to CET (Europe/Berlin)
tz = ZoneInfo("Europe/Berlin")

# List of sample questions and answers
SAMPLE_QUESTIONS = [
    # RELEVANT
    "What can I cook with chicken and broccoli?",
    "Can you suggest a quick and easy vegetarian meal?",
    "I have some tomatoes and pasta. What dish can I make?",
    "What are some good recipes for a 30-minute dinner?",
    "I'm craving Indian food. Any recipe suggestions?",
    
    # PARTLY RELEVANT
    "Can you recommend a healthy recipe that includes beans?",
    "What's a good dessert recipe for someone who loves chocolate?",
    "What are some interesting ways to use spinach in a meal?",
    
    # NON RELEVANT
    "How do I fix a flat tire?",
    "Can you recommend a good book to read?",
    "What's the best way to clean a house?",
    
    # NOT RELEVANT
    "Tell me a joke.",
    "How do I change a light bulb?",
    "Can you give me a summary of the latest tech news?"
]

# Sample answers
SAMPLE_ANSWERS = [
    # RELEVANT
    "You can make a chicken and broccoli stir-fry. Just sauté chicken pieces with garlic, add broccoli, and season with soy sauce. Serve with rice or noodles.",
    "How about a vegetable stir-fry? Just sauté your favorite vegetables like bell peppers, carrots, and broccoli with soy sauce and serve with rice or noodles.",
    "You could make a tomato and pasta dish. Cook the pasta, then mix with a simple tomato sauce made from sautéed garlic, tomatoes, and basil.",
    "Try making a quick stir-fry with your choice of protein and vegetables. Add soy sauce, garlic, and ginger for flavor. Serve over rice or noodles.",
    "Consider making a paneer tikka masala. Marinate paneer cubes in yogurt and spices, then cook with a tomato-based sauce.",
    
    # PARTLY RELEVANT
    "You can make a black bean salad. Mix black beans with corn, avocado, cherry tomatoes, and a lime vinaigrette.",
    "Try making a chocolate avocado mousse. Blend ripe avocados with cocoa powder, a bit of honey, and vanilla extract until smooth.",
    "How about a spinach and feta omelette? Just whisk eggs, pour into a pan, and add fresh spinach and feta cheese before folding.",
    
    # NON RELEVANT
    "This is not related to cooking, but to fix a flat tire, you need to remove the tire, find the puncture, and either patch or replace it.",
    "This is not related to cooking. A good book recommendation would be 'To Kill a Mockingbird' by Harper Lee.",
    "This is not related to cooking. The best way to clean a house is to organize tasks and use appropriate cleaning supplies for each area.",
    
    # NOT RELEVANT
    "Here's a joke: Why did the chef break up with the cookbook? Because it had too many problems!",
    "This is not related to cooking. To change a light bulb, make sure the power is off, then twist the old bulb out and screw in the new one.",
    "This is not related to cooking. To get a summary of the latest tech news, check out tech news websites or apps."
]

MODELS = ["ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"]
RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def generate_synthetic_data(start_time, end_time):
    current_time = start_time
    conversation_count = 0
    print(f"Starting historical data generation from {start_time} to {end_time}")
    while current_time < end_time:
        conversation_id = str(uuid.uuid4())
        question = random.choice(SAMPLE_QUESTIONS)
        answer = random.choice(SAMPLE_ANSWERS)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

        openai_cost = 0

        if model.startswith("openai/"):
            openai_cost = random.uniform(0.001, 0.1)

        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 5.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} to the question.",
            "model_used": model,
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(50, 300),
            "total_tokens": random.randint(100, 500),
            "eval_prompt_tokens": random.randint(50, 150),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 250),
            "openai_cost": openai_cost,
        }

        save_conversation(conversation_id, question, answer_data, current_time)
        print(
            f"Saved conversation: ID={conversation_id}, Time={current_time}, Model={model}"
        )

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time)
            print(
                f"Saved feedback for conversation {conversation_id}: {'Positive' if feedback > 0 else 'Negative'}"
            )

        current_time += timedelta(minutes=random.randint(1, 15))
        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} conversations so far...")

    print(
        f"Historical data generation complete. Total conversations: {conversation_count}"
    )


def generate_live_data():
    conversation_count = 0
    print("Starting live data generation...")
    while True:
        current_time = datetime.now(tz)
        # current_time = None
        conversation_id = str(uuid.uuid4())
        question = random.choice(SAMPLE_QUESTIONS)
        answer = random.choice(SAMPLE_ANSWERS)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

        openai_cost = 0

        if model.startswith("openai/"):
            openai_cost = random.uniform(0.001, 0.1)

        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 5.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} to the question.",
            "model_used": model,
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(50, 300),
            "total_tokens": random.randint(100, 500),
            "eval_prompt_tokens": random.randint(50, 150),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 250),
            "openai_cost": openai_cost,
        }

        save_conversation(conversation_id, question, answer_data, current_time)
        print(
            f"Saved live conversation: ID={conversation_id}, Time={current_time}, Model={model}"
        )

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time)
            print(
                f"Saved feedback for live conversation {conversation_id}: {'Positive' if feedback > 0 else 'Negative'}"
            )

        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} live conversations so far...")

        time.sleep(1)


if __name__ == "__main__":
    get_db_connection()
    print(f"Script started at {datetime.now(tz)}")
    end_time = datetime.now(tz)
    start_time = end_time - timedelta(hours=6)
    print(f"Generating historical data from {start_time} to {end_time}")
    generate_synthetic_data(start_time, end_time)
    print("Historical data generation complete.")

    print("Starting live data generation... Press Ctrl+C to stop.")
    try:
        generate_live_data()
    except KeyboardInterrupt:
        print(f"Live data generation stopped at {datetime.now(tz)}.")
    finally:
        print(f"Script ended at {datetime.now(tz)}")
