"""Blackboard shared context implementation.

This module provides a lightweight Blackboard for the course project.
All agents can read the full shared context, but each agent can only
update its own field.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class BlackboardPermissionError(Exception):
    """Raised when an agent tries to update a field it does not own."""


class Blackboard:
    """Unified shared context for multi-agent collaboration.

    Supported fields:
    - emotion
    - persona
    - imagery
    - memory
    """

    _AGENT_FIELD_MAP = {
        "emotion_agent": "emotion",
        "persona_agent": "persona",
        "imagery_agent": "imagery",
        "memory_agent": "memory",
    }

    _VALID_FIELDS = set(_AGENT_FIELD_MAP.values())

    def __init__(self) -> None:
        self._context = {
            "emotion": {},
            "persona": {},
            "imagery": {},
            "memory": {},
        }

    def update(self, agent_name: str, data: dict[str, Any]) -> None:
        """Update the field owned by the given agent.

        Args:
            agent_name: Agent identifier, such as ``emotion_agent``.
            data: Structured result data produced by the agent.

        Raises:
            BlackboardPermissionError: If the agent is not allowed to update.
            TypeError: If data is not a dictionary.
        """
        if agent_name not in self._AGENT_FIELD_MAP:
            raise BlackboardPermissionError(
                f"Agent '{agent_name}' is not allowed to update the blackboard."
            )

        if not isinstance(data, dict):
            raise TypeError("Blackboard update data must be a dictionary.")

        field_name = self._AGENT_FIELD_MAP[agent_name]
        self._context[field_name] = deepcopy(data)

    def read(self, field_name: str | None = None) -> dict[str, Any]:
        """Read the full blackboard or a single field.

        Args:
            field_name: Optional field name. If omitted, return the full context.

        Returns:
            A deep copy of the requested data.

        Raises:
            ValueError: If the requested field does not exist.
        """
        if field_name is None:
            return deepcopy(self._context)

        if field_name not in self._VALID_FIELDS:
            raise ValueError(f"Field '{field_name}' is not defined in blackboard.")

        return deepcopy(self._context[field_name])

    def clear(self) -> None:
        """Reset all fields to empty dictionaries."""
        for field_name in self._context:
            self._context[field_name] = {}
