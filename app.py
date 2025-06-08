import streamlit as st
import os
from datetime import datetime
from rag import NewsRAG, initialize_rag

# Set page configuration
st.set_page_config(
    page_title="Bangladesh News Assistant",
    page_icon="📰",
    layout="wide"
)

# Initialize session state
if 'rag' not in st.session_state:
    st.session_state.rag = initialize_rag()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# App title
st.title("Bangladesh News Assistant")

# Sidebar 
with st.sidebar:
    if st.button("🔄 Update News Data"):
        with st.spinner("Scraping latest news from Bangladeshi sources..."):
            result = st.session_state.rag.refresh_news()
            st.success(result)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app uses AI to answer your questions about recent news from Bangladesh. [Developed by Rakesh Debnath]
    
    Data is collected from:
    - The Daily Star
    - Prothom Alo (English)

    Powered by:
    - LangChain
    - Google Gemini AI
    - ChromaDB
    - Streamlit
    """)

    # Display last updated date
    latest_file = st.session_state.rag.find_latest_news_file()
    if latest_file:
        raw_date = os.path.basename(latest_file).replace("news_articles_", "").replace(".json", "")
        try:
            formatted_date = datetime.strptime(raw_date, "%Y%m%d").strftime("%d-%m-%Y")
            st.info(f"📅 News last updated: {formatted_date}")
        except ValueError:
            st.warning("⚠️ Could not parse news date.")
    else:
        st.warning("No news data available. Click 'Refresh News' to get started.")


# Main chat interface
st.markdown("### Ask about recent news from Bangladesh")

def clear_question_field():
    st.session_state.user_question = ""

user_question = st.text_input("Your question:", key="user_question")
col1, col2 = st.columns(2)
if col1.button("Ask"):   
    if user_question:
        if user_question != st.session_state.get("last_question", ""):
            st.session_state.last_question = user_question
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.spinner("Searching news and generating answer..."):
                response = st.session_state.rag.query(user_question)
                answer = response.get("answer", "Sorry, I couldn't find an answer based on recent news.")
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            
col2.button("Clear", on_click=clear_question_field)
            

# Display chat history
st.markdown("### Conversation")
history = st.session_state.chat_history
for i in range(len(history) - 1, 0, -2):
    user_msg = history[i-1]
    assistant_msg = history[i]
    if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
        st.markdown(f"**You:** {user_msg['content']}")
        st.markdown(f"**News Assistant:** {assistant_msg['content']}")
        st.markdown("---")
    else:
        # fallback if message roles are not as expected (just display individually)
        st.markdown(f"**{user_msg['role'].capitalize()}:** {user_msg['content']}")
        st.markdown(f"**{assistant_msg['role'].capitalize()}:** {assistant_msg['content']}")
        st.markdown("---")



