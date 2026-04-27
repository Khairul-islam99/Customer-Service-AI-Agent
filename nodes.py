import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from state import AgentState
from tools import search_available_properties, get_listing_details, create_booking

load_dotenv()

# Setup LLM using OpenRouter and Nvidia Nemotron model
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="nvidia/nemotron-3-nano-30b-a3b:free",
)
# Bind tools to the LLM
tools = [search_available_properties, get_listing_details, create_booking]
llm_with_tools = llm.bind_tools(tools)


# ToolNode automatically executes the tools when called by the LLM


tool_node = ToolNode(tools)

def escalation_check_node(state: AgentState) -> dict:
    """Checks if the user's request needs to be escalated to a human."""
    messages = state.get("messages", [])
    if not messages:
        return {"escalate_to_human": False}
    
    last_msg = messages[-1].content.lower()
    
    # Keywords that trigger escalation
    keywords = ["refund", "complaint", "manager", "broken", "human"]
    escalate = any(k in last_msg for k in keywords)
    
    return {"escalate_to_human": escalate}

def agent_node(state: AgentState) -> dict:
    """Invokes the LLM to generate a response or call a tool."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}