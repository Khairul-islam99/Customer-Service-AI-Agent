from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from graph import graph

app = FastAPI(title="StayEase AI Agent API")

# Simple in-memory storage for chat history
chat_histories = {}

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    reply: str
    escalated: bool

@app.post("/api/chat/{conversation_id}/message", response_model=MessageResponse)
def send_message(conversation_id: str, request: MessageRequest):
    if conversation_id not in chat_histories:
        chat_histories[conversation_id] = []
        
    chat_histories[conversation_id].append(HumanMessage(content=request.message))
    
    try:
        # Run the LangGraph agent
        result = graph.invoke({"messages": chat_histories[conversation_id]})
        
        final_messages = result.get("messages", [])
        last_message = final_messages[-1].content
        escalated = result.get("escalate_to_human", False)
        
        # Update history
        chat_histories[conversation_id] = final_messages
        
        return MessageResponse(reply=last_message, escalated=escalated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{conversation_id}/history")
def get_history(conversation_id: str):
    if conversation_id not in chat_histories:
        return {"history": []}
    
    formatted_history = []
    for msg in chat_histories[conversation_id]:
        role = "guest" if isinstance(msg, HumanMessage) else "agent"
        formatted_history.append({"role": role, "content": msg.content})
        
    return {"history": formatted_history}