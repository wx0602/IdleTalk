"""Request models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming request for the chat endpoint."""

    user_input: str = Field(..., min_length=1, description="User input text")
    user_id: str = Field(
        default="default_user",
        min_length=1,
        description="User identifier for memory storage",
    )
