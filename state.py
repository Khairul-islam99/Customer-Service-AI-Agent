from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# memory of the agent
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    escalate_to_human: bool