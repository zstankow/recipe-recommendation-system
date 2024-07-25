import streamlit as st
import uuid
import time
from assistant import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats

def print_log(message):
    print(message, flush=True)

def main():
    st.title("RAG Recipe Assistant")

    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")
    if 'count' not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")
    
    # Model choice
    model_choice = st.selectbox(
        "Select a model:",
        ["ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"]
    )
    print_log(f"User selected model: {model_choice}")

    # Search type choice
    search_type = st.radio(
        "Select search type:",
        ["Text", "Vector"]
    )
    print_log(f"User selected search type: {search_type}")

    # User input
    user_input = st.text_input("Enter your query. (Hint: What do you feel like eating? What ingredients do you have? How much time do you have?)")
    if st.button("Ask"):
        print_log(f"User asked: '{user_input}'")
        start_time = time.time()
        answer_data = get_answer(user_input, model_choice, search_type)
        end_time = time.time()
        print_log(f"Answer received in {end_time - start_time:.2f} seconds")
        st.success("Completed!")
        st.write(answer_data['answer'])

    # Monitering information
    st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
    st.write(f"Relevance: {answer_data['relevance']}")
    st.write(f"Model used: {answer_data['model_used']}")
    st.write(f"Total tokens: {answer_data['total_tokens']}")
    if answer_data['openai_cost'] > 0:
        st.write(f"OpenAI cost: ${answer_data['openai_cost']:.4f}")

    # Save conversation to database
    print_log("Saving conversation to database")
    save_conversation(st.session_state.conversation_id, user_input, answer_data)
    print_log("Conversation saved successfully")

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1"):
            st.session_state.count += 1
            print_log(f"Positive feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, 1)
            print_log("Positive feedback saved to database")
    with col2:
        if st.button("-1"):
            st.session_state.count -= 1
            print_log(f"Negative feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, -1)
            print_log("Negative feedback saved to database")

    st.write(f"Current count: {st.session_state.count}")

    # Displaying conversation history
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox("Filter by relevance:", ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"])
    recent_conversations = get_recent_conversations(limit=5, relevance=relevance_filter if relevance_filter != "All" else None)
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write(f"Relevance: {conv['relevance']}")
        st.write(f"Model: {conv['model_used']}")
        st.write("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")

print_log("Streamlit app loop completed")

if __name__ == "__main__":
    print_log("Course Assistant application started")
    main()