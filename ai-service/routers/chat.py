"""
Chat Router
Exposes the Conversational Orchestrator to the frontend via API.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from services.orchestrator import OrchestratorService, ChatMessage, OrchestratorResponse

router = APIRouter(
    prefix="/api/v2/chat",
    tags=["V2 Chat"],
    responses={404: {"description": "Not found"}}
)

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@router.post("/", response_model=OrchestratorResponse)
async def chat_with_nova(request: ChatRequest):
    """
    Send a message to Nova and get a conversational response + actions.
    """
    orchestrator = OrchestratorService()
    try:
        response = await orchestrator.process_message(request.messages)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_with_nova_stream(request: ChatRequest):
    """
    Stream a message to Nova and get SSE events.
    """
    orchestrator = OrchestratorService()
    return StreamingResponse(
        orchestrator.process_message_stream(request.messages),
        media_type="text/event-stream"
    )
