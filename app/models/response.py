"""Response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatDisplay(BaseModel):
    """Frontend-friendly display block."""

    text: str = Field(default="")
    emotion: str = Field(default="")
    tone: str = Field(default="")
    imagery: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Unified response for the chat endpoint."""

    status: str = Field(default="success")
    user_input: str = Field(default="")
    final_response: str = Field(default="")
    display: ChatDisplay = Field(default_factory=ChatDisplay)
    context: dict[str, Any] = Field(default_factory=dict)
    trace: dict[str, Any] = Field(default_factory=dict)
