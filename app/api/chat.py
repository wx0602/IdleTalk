"""Chat API router."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.service.conversation_service import ConversationService

router = APIRouter()
conversation_service = ConversationService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Receive user input and return the final multi-agent response."""
    try:
        result = conversation_service.run_chat(
            user_input=request.user_input,
            user_id=request.user_id,
        )
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
