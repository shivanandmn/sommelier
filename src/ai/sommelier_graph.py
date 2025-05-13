"""
Sommelier Graph implementation using LangGraph.

This module implements a multi-agent sommelier system using LangGraph for orchestration.
Each agent in the system has defined roles, responsibilities, and specialized knowledge
to ensure the highest standard of conversational wine service.
"""
from typing import Dict, Any, List, TypedDict, Annotated, Literal, Union, cast
import json
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
# No need for ToolExecutor import as it's not used
# from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint import MemorySaver
from langchain.globals import set_debug
set_debug(True)
# Import our agent types
from .agents.agent_types import AGENT_ROLES


# Define the state for our graph
class SommelierState(TypedDict):
    """State for the sommelier graph."""
    # The original query from the user
    query: str
    # The current conversation history
    conversation: List[Union[HumanMessage, AIMessage, SystemMessage]]
    # The current agent processing the query
    current_agent: str
    # Responses from each agent
    agent_responses: Dict[str, str]
    # Additional context for processing
    context: Dict[str, Any]
    # Final response to return to the user
    final_response: str


def create_agent_node(agent_type: str):
    """
    Create a node function for a specific agent type.
    
    Args:
        agent_type: The type of agent to create a node for
        
    Returns:
        A function that processes the state for this agent type
    """
    def agent_node(state: SommelierState) -> SommelierState:
        """Process the state for this agent type."""
        # Get the agent role information
        agent_role = AGENT_ROLES[agent_type]
        
        # Create the system prompt
        system_prompt = agent_role["system_prompt"]
        
        # Create the conversation history for this agent
        messages = [SystemMessage(content=system_prompt)]
        
        # Add the conversation history
        messages.extend(state["conversation"])
        
        # Add any context information if available
        if state["context"]:
            context_str = json.dumps(state["context"], indent=2)
            messages.append(SystemMessage(content=f"Additional context:\n{context_str}"))
        
        # Create the LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        # Get the response from the LLM
        response = llm.invoke(messages)
        
        # Update the agent responses
        updated_responses = state["agent_responses"].copy()
        updated_responses[agent_type] = response.content
        
        # Return the updated state
        return {
            **state,
            "agent_responses": updated_responses,
            "current_agent": agent_type
        }
    
    return agent_node


def route_query(state: SommelierState) -> str:
    """
    Route the query to the appropriate agent based on the content.
    
    Args:
        state: The current state of the conversation
        
    Returns:
        The name of the agent to route to
    """
    # Get the query
    query = state["query"]
    
    # Create the LLM for routing
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create the prompt for routing
    prompt = f"""Analyze the following user query and determine which wine specialist agent should handle it:

User Query: {query}

Available agents:
1. Wine Knowledge Specialist - For questions about grape varieties, appellations, production techniques, vintages, aging potential
2. Food Pairing Expert - For questions about pairing wine with food
3. Storyteller - For requests seeking engaging stories or descriptions about wines
4. Sales Strategist - For inquiries about pricing, deals, or purchasing recommendations
5. Inventory Coordinator - For questions about availability, shipping, or logistics
6. Preference Tracker - For personalized recommendations based on past preferences

Respond with ONLY ONE of these exact agent names:
- wine_knowledge
- food_pairing
- storyteller
- sales
- inventory
- preferences

Your response should be just the agent name, nothing else."""
    
    # Get the routing decision
    response = llm.invoke([HumanMessage(content=prompt)])
    agent = response.content.strip().lower()
    
    # Default to wine_knowledge if we get an invalid response
    if agent not in AGENT_ROLES:
        agent = "wine_knowledge"
    
    return agent


def orchestrate_responses(state: SommelierState) -> SommelierState:
    """
    Orchestrate the responses from all agents into a coherent response.
    
    Args:
        state: The current state of the conversation
        
    Returns:
        The updated state with a final response
    """
    # Get the current agent and its response
    current_agent = state["current_agent"]
    agent_response = state["agent_responses"][current_agent]
    
    # Create the LLM for orchestration
    orchestrator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Create the prompt for orchestration
    orchestrator_prompt = f"""You are the Dialogue Orchestrator for a wine sommelier service.
    
    The user asked: {state['query']}
    
    The {current_agent} agent provided this response:
    {agent_response}
    
    Your job is to take this response and create a coherent, well-structured response that contains all the important information.
    Maintain the factual information and recommendations, but make the tone warm and engaging.
    Focus on being persuasive and helpful.
    """
    
    # Get the orchestrated response
    orchestrator_messages = [SystemMessage(content=orchestrator_prompt)]
    orchestrator_response = orchestrator_llm.invoke(orchestrator_messages)
    
    # Now, have the concise_human agent transform it into a brief, conversational response
    concise_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
    
    # Create the prompt for the concise human agent
    concise_system_prompt = AGENT_ROLES["concise_human"]["system_prompt"]
    
    concise_prompt = f"{concise_system_prompt}\n\nThe user asked: {state['query']}\n\nDetailed response: {orchestrator_response.content}\n\nTransform this into a brief, human-like response while preserving the key information and maintaining a persuasive tone."
    
    # Get the concise response
    concise_messages = [SystemMessage(content=concise_prompt)]
    concise_response = concise_llm.invoke(concise_messages)
    
    # Update the agent responses
    updated_responses = state["agent_responses"].copy()
    updated_responses["orchestrator"] = orchestrator_response.content
    updated_responses["concise_human"] = concise_response.content
    
    # Return the updated state with the final response
    return {
        **state,
        "agent_responses": updated_responses,
        "final_response": concise_response.content,
        "current_agent": "orchestrator"
    }


def process_concise_human(state: SommelierState) -> SommelierState:
    """
    Process the orchestrated response through the concise human agent.
    
    Args:
        state: The current state of the conversation
        
    Returns:
        The updated state with a concise, human-like response
    """
    # Get the orchestrated response
    orchestrated_response = state["agent_responses"]["orchestrator"]
    
    # Create the LLM for the concise human agent
    concise_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
    
    # Create the prompt for the concise human agent
    concise_system_prompt = AGENT_ROLES["concise_human"]["system_prompt"]
    
    concise_prompt = f"{concise_system_prompt}\n\nThe user asked: {state['query']}\n\nDetailed response: {orchestrated_response}\n\nTransform this into a brief, human-like response while preserving the key information and maintaining a persuasive tone."
    
    # Get the concise response
    concise_messages = [SystemMessage(content=concise_prompt)]
    concise_response = concise_llm.invoke(concise_messages)
    
    # Update the agent responses
    updated_responses = state["agent_responses"].copy()
    updated_responses["concise_human"] = concise_response.content
    
    # Return the updated state
    return {
        **state,
        "agent_responses": updated_responses,
        "final_response": concise_response.content,
        "current_agent": "concise_human"
    }


def create_sommelier_graph() -> StateGraph:
    """
    Create the sommelier graph.
    
    Returns:
        The configured StateGraph for the sommelier system
    """
    # Create the workflow
    workflow = StateGraph(SommelierState)
    
    # Add the empty start node
    workflow.add_node("", lambda x: x)
    
    # Add nodes for each agent type except orchestrator and concise_human
    for agent_type in AGENT_ROLES:
        if agent_type not in ["orchestrator", "concise_human"]:
            workflow.add_node(agent_type, create_agent_node(agent_type))
    
    # Add the orchestrator node separately
    workflow.add_node("orchestrator", orchestrate_responses)
    
    # Add conditional edges from the start node to each agent
    workflow.add_conditional_edges(
        "",
        route_query,
        {
            agent_type: agent_type for agent_type in AGENT_ROLES 
            if agent_type not in ["orchestrator", "concise_human"]
        }
    )
    
    # Add edges from each agent to the orchestrator
    for agent_type in AGENT_ROLES:
        if agent_type not in ["orchestrator", "concise_human"]:
            workflow.add_edge(agent_type, "orchestrator")
    
    # Add the edge from the orchestrator to the end
    workflow.add_edge("orchestrator", END)
    
    # Set the entry point
    workflow.set_entry_point("")
    
    return workflow


class SommelierChat:
    """
    Main class for interacting with the sommelier graph.
    
    This class provides a simple interface for sending queries to the
    sommelier graph and getting responses.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the sommelier chat.
        
        Args:
            model_name: The OpenAI model to use
            temperature: The temperature setting for the model
        """
        # Create the graph
        self.graph = create_sommelier_graph().compile()
        
        # Create a memory saver for persistence
        self.memory = MemorySaver()
        
        # Store the model parameters
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialize the conversation history
        self.conversation = []
        
        # Initialize the context
        self.context = {}
    
    def get_response(self, query: str):
        """
        Get a response from the sommelier graph.
        
        Args:
            query: The user's query
            
        Returns:
            The response from the sommelier graph
        """
        # Add the query to the conversation history
        self.conversation.append(HumanMessage(content=query))
        
        # Create the initial state
        state = {
            "query": query,
            "conversation": self.conversation,
            "current_agent": "",
            "agent_responses": {},
            "context": self.context,
            "final_response": ""
        }
        
        # Run the graph
        result = self.graph.invoke(state)
        
        # Get the final response
        response = result["final_response"]
        
        # Add the response to the conversation history
        self.conversation.append(AIMessage(content=response))
        
        # Return the response
        return response
    
    def stream_response(self, query: str):
        """
        Stream a response from the sommelier graph.
        
        Args:
            query: The user's query
            
        Yields:
            Chunks of the response from the sommelier graph
        """
        # Get the full response
        response = self.get_response(query)
        
        # Simulate streaming by yielding individual characters or small groups
        # This provides a more natural streaming experience
        # In a real implementation, we would use a streaming API
        
        # Option 1: Stream character by character for a smooth effect
        for char in response:
            yield char
            
        # Alternative options (commented out):
        # Option 2: Stream word by word
        # words = response.split()
        # for i, word in enumerate(words):
        #     # Add space before words except the first one
        #     if i > 0:
        #         yield " " + word
        #     else:
        #         yield word
    
    def add_context(self, key: str, value: Any):
        """
        Add context information for the agents.
        
        Args:
            key: The context key
            value: The context value
        """
        self.context[key] = value
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation = []
    
    def clear_context(self):
        """Clear the context."""
        self.context = {}
