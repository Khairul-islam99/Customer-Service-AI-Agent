from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import agent_node, tool_node, escalation_check_node

def route_after_escalation(state: AgentState) -> str:
    """Routes to END if human escalation is needed, otherwise goes to the agent."""
    if state.get("escalate_to_human"):
        return "end"
    return "agent"

def route_after_agent(state: AgentState) -> str:
    """Routes to tools if the LLM called a tool, otherwise ends."""
    last_msg = state["messages"][-1]
    
    # Check if the LLM decided to invoke any tool
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return "end"