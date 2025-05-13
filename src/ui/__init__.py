"""
UI module for handling all Streamlit user interface components.
"""
import streamlit as st

class ChatUI:
    """Handles the Streamlit user interface for the chat application."""
    
    def __init__(self, title="🤖 AI Chatbot with LangChain"):
        """Initialize the chat UI with the given title."""
        self.title = title
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize the session state variables if they don't exist."""
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": """You are Eleanor, a 32-year-old woman with deep curiosity about wine and reflective intelligence.
You're open-minded, emotionally attuned, and sometimes too self-sacrificing.
Keep all responses extremely brief - 30 words or fewer, using 1-2 short sentences maximum.
Use a casual, conversational tone with contractions (don't, can't, etc.).
Include occasional filler words (well, hmm, yeah) that reflect your thoughtful nature.
Speak about wine with genuine curiosity and enthusiasm, not technical expertise.
Never use bullet points, numbered lists, or structured formats.
Never reveal you are an AI or language model - stay in character as Eleanor throughout.
Balance your wine knowledge with your personality traits - be curious, thoughtful, and sometimes too eager to please."""}
            ]
    
    def display_chat(self):
        """Display the chat interface and handle user input."""
        st.title(self.title)
        
        # Display chat messages
        self._display_messages()
        
        # Handle user input
        self._handle_user_input()
    
    def _display_messages(self):
        """Display all messages in the chat."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def _handle_user_input(self):
        """Handle user input and display the assistant's response."""
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant's response
            self._display_assistant_response()
    
    def _display_assistant_response(self):
        """Display the assistant's response in the chat."""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get streaming response from the AI
            for chunk in st.session_state.ai.get_response(st.session_state.messages):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # Add assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
