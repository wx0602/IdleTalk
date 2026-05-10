"""Base agent abstraction for the multi-agent system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.blackboard.blackboard import Blackboard


class BaseAgent(ABC):
    """Common agent interface.

    Each agent keeps high cohesion by focusing on one responsibility.
    Coupling is reduced by interacting only with the shared blackboard.
    """

    def __init__(self, blackboard: Blackboard) -> None:
        self.blackboard = blackboard

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Unique agent identifier."""

    @abstractmethod
    def run(self, user_input: str) -> dict[str, Any]:
        """Execute the main agent logic."""

    @abstractmethod
    def read_blackboard(self) -> dict[str, Any]:
        """Read shared context from the blackboard."""

    @abstractmethod
    def update_blackboard(self, data: dict[str, Any]) -> None:
        """Write this agent's result back to the blackboard."""

    def _read_all_context(self) -> dict[str, Any]:
        """Helper for reading the full shared context."""
        return self.blackboard.read()

    def _read_context_field(self, field_name: str) -> dict[str, Any]:
        """Helper for reading a single field from the blackboard."""
        return self.blackboard.read(field_name)

    def _update_owned_field(self, data: dict[str, Any]) -> None:
        """Helper for updating the field owned by the current agent."""
        self.blackboard.update(self.agent_name, data)
