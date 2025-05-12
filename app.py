import os
from dotenv import load_dotenv
import streamlit as st
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("Please set the OPENAI_API_KEY in the .env file")
    st.stop()

# Set up the language model
llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")

# Define the state structure for our chatbot
class ChatState:
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

# Initialize session state
if "chat_state" not in st.session_state:
    st.session_state.chat_state = ChatState()
    st.session_state.chat_state.add_message("assistant", "Hello! I'm your AI assistant. How can I help you today?")

# Define the nodes for our graph
def generate_response(state):
    # Convert messages to the format expected by the model
    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in state.messages
    ]
    
    # Get response from the model
    response = llm.invoke(messages)
    
    # Add the response to the state
    state.add_message("assistant", response.content)
    return state

# Define the edges
def should_continue(state):
    # In a real application, you might have more complex logic here
    # to determine if the conversation should continue
    return "end"

# Create the graph
workflow = StateGraph(ChatState)

# Add nodes
workflow.add_node("generate", generate_response)
workflow.set_entry_point("generate")

# Add conditional edges
workflow.add_conditional_edges(
    "generate",
    should_continue,
    {
        "end": END,
    },
)

# Compile the graph
app = workflow.compile()

# Streamlit UI
st.title("🤖 AI Chatbot with LangGraph")

# Display chat messages
for msg in st.session_state.chat_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.chat_state.add_message("user", prompt)
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream the response
        for chunk in app.stream(st.session_state.chat_state):
            if "generate" in chunk and "messages" in chunk["generate"]:
                full_response = chunk["generate"]["messages"][-1]["content"]
                response_placeholder.markdown(full_response)
    
    # Update the chat state with the assistant's response
    st.session_state.chat_state.add_message("assistant", full_response)
    
    # Rerun to update the chat display
    st.rerun()
