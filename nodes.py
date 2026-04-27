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