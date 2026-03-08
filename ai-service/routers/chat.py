"""
Chat Router
Exposes the Conversational Orchestrator to the frontend via API.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from services.orchestrator import OrchestratorService, ChatMessage, OrchestratorResponse
from datetime import datetime
import logging

router = APIRouter(
    prefix="/api/v2/chat",
    tags=["V2 Chat"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)
PROMPT_LOG_FILE = "prompt_log.txt"

def get_user_id(http_request: Request) -> str:
    """Get user identifier from session ID header sent by the frontend."""
    return http_request.headers.get("X-Session-ID", "unknown")

def log_prompt(messages: List[ChatMessage], user_ip: str = "unknown"):
    """Log the latest user prompt to terminal and prompt_log.txt."""
    user_messages = [m for m in messages if m.role == "user"]
    if not user_messages:
        return
    latest = user_messages[-1].content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{user_ip}] {latest}"
    logger.info(f"USER PROMPT [{user_ip}]: {latest}")
    with open(PROMPT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@router.post("/", response_model=OrchestratorResponse)
async def chat_with_nova(request: ChatRequest, http_request: Request):
    """
    Send a message to Nova and get a conversational response + actions.
    """
    user_ip = get_user_id(http_request)
    log_prompt(request.messages, user_ip)
    orchestrator = OrchestratorService()
    try:
        response = await orchestrator.process_message(request.messages)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_with_nova_stream(request: ChatRequest, http_request: Request):
    """
    Stream a message to Nova and get SSE events.
    """
    user_ip = get_user_id(http_request)
    log_prompt(request.messages, user_ip)
    orchestrator = OrchestratorService()
    return StreamingResponse(
        orchestrator.process_message_stream(request.messages),
        media_type="text/event-stream"
    )
