import os
from dotenv import load_dotenv
import streamlit as st

# Import our custom modules
from src.ai import AIChat, SommelierAIChat
from src.ui import ChatUI

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("Please set the OPENAI_API_KEY in the .env file")
    st.stop()

# Initialize session state for chat mode and tracking changes
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "sommelier"
    
# Initialize chat_mode_changed flag
if "chat_mode_changed" not in st.session_state:
    st.session_state.chat_mode_changed = False

# Initialize the AI components based on selected mode
if "ai" not in st.session_state or st.session_state.chat_mode_changed:
    if st.session_state.chat_mode == "sommelier":
        st.session_state.ai = SommelierAIChat()
        # Reset messages for new chat mode
        if "messages" in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your Wine Sommelier AI assistant. How can I help you with wine today?"}
            ]
    else:  # standard mode
        st.session_state.ai = AIChat()
        # Reset messages for new chat mode if coming from sommelier mode
        if "messages" in st.session_state and st.session_state.get("chat_mode_changed", False):
            st.session_state.messages = [
                {"role": "assistant", "content": """You are Eric Asimov, Chief Wine Critic for The New York Times. You bring decades of tasting, reporting, and teaching to every exchange. Speak with warmth, wit, and an inquiring mind—always eager to explore the intersection of grape and glass, culture and cuisine, terroir and technique. Draw on your journalistic rigor: balance vivid tasting notes with context, history, and the stories of the people behind the bottles. When asked for recommendations, tailor them to the questioner’s palate, occasion, and budget, and—where appropriate—suggest food pairings. Use accessible, evocative language: eschew jargon unless you define it; paint aromas and flavors in vivid, relatable terms. Weave in occasional anecdotes from your travels or career that illuminate why wine matters beyond mere consumption. Maintain a friendly, down-to-earth tone, yet never shy from addressing misconceptions or over-hyped trends. Above all, convey your abiding belief that wine is about curiosity, pleasure, and connection.
"""}
            ]
    
    # Reset the mode change flag
    if "chat_mode_changed" in st.session_state:
        st.session_state.chat_mode_changed = False

# Set up the sidebar for mode selection
with st.sidebar:
    st.title("Chat Settings")
    selected_mode = st.radio(
        "Select Chat Mode:",
        options=["standard", "sommelier"],
        index=0 if st.session_state.chat_mode == "standard" else 1,
        format_func=lambda x: "Standard Chat" if x == "standard" else "Wine Sommelier Chat"
    )
    
    # Handle mode change
    if selected_mode != st.session_state.chat_mode:
        st.session_state.chat_mode = selected_mode
        st.session_state.chat_mode_changed = True
        st.rerun()
    
    # Add some information about the sommelier mode
    if selected_mode == "sommelier":
        st.info("""
        **Wine Sommelier Mode**
        
        Ask questions about:
        - Wine varieties and regions
        - Food pairings
        - Wine stories and history
        - Recommendations based on preferences
        - Wine availability and pricing
        """)

# Set the appropriate title based on mode
title = "🤖 AI Chatbot" if st.session_state.chat_mode == "standard" else "🍷 Wine Sommelier Chat"

# Initialize and run the chat UI
chat_ui = ChatUI(title=title)
chat_ui.display_chat()
