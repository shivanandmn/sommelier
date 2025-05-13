"""
AI module for handling all AI-related functionality.
"""
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
from .sommelier_graph import SommelierChat

class AIChat:
    """Handles AI chat functionality using LangChain and OpenAI."""
    
    def __init__(self, model_name="gpt-4o-mini", temperature=0.7):
        """Initialize the AI chat with the specified model and temperature."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.llm = ChatOpenAI(
            temperature=temperature,
            model=model_name,
            streaming=True,
        )
    
    def get_response(self, messages):
        """
        Get a streaming response from the AI model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Yields:
            Chunks of the AI response
        """
        messages_for_llm = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        for chunk in self.llm.stream(messages_for_llm):
            if chunk.content is not None:
                yield chunk.content

class SommelierAIChat:
    """Adapter class that integrates SommelierChat with the UI chatbot interface."""
    
    def __init__(self, model_name="gpt-4o-mini", temperature=0.7):
        """Initialize the Sommelier AI chat with the specified model and temperature."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.sommelier = SommelierChat(
            model_name=model_name,
            temperature=temperature
        )
        self._convert_history_to_sommelier()
    
    def _convert_history_to_sommelier(self):
        """Convert existing session history to sommelier format if needed."""
        # This would be called when switching from standard chat to sommelier chat
        # Currently just initializes an empty history since we're starting fresh
        self.sommelier.clear_conversation()
    
    def get_response(self, messages):
        """
        Get a streaming response from the Sommelier AI.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Yields:
            Chunks of the Sommelier AI response
        """
        # Extract the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        if not last_user_message:
            yield "I'm sorry, I couldn't find your question. How can I help you with wine today?"
            return
        
        # Use the stream_response method from SommelierChat
        for chunk in self.sommelier.stream_response(last_user_message):
            yield chunk
    
    def add_context(self, key, value):
        """Add context information to the Sommelier chat."""
        self.sommelier.add_context(key, value)
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.sommelier.clear_conversation()
