"""Memory agent implementation."""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.data_access.memory_repository import MemoryRepository


class MemoryAgent(BaseAgent):
    """Read and update user preferences with simple rules."""

    _PREFERENCE_HINTS = ["喜欢", "偏好", "希望", "想要", "最好", "更喜欢"]

    _IMAGERY_OPTIONS = [
        "菜市场",
        "热汤",
        "雨",
        "河流",
        "小馆子",
        "夏天",
        "食物",
        "灯火",
        "街巷",
        "院子",
        "草木",
    ]

    _EMOTION_STYLE_OPTIONS = [
        "温和",
        "平静",
        "克制",
        "怀旧",
        "安静",
        "安慰",
        "温润",
        "平实",
    ]

    def __init__(
        self,
        blackboard,
        memory_repository: MemoryRepository | None = None,
        user_id: str = "default_user",
    ) -> None:
        super().__init__(blackboard)
        self.memory_repository = memory_repository or MemoryRepository()
        self.user_id = user_id

    @property
    def agent_name(self) -> str:
        return "memory_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        _ = self.read_blackboard()
        history = self.memory_repository.get_user_memory(self.user_id)
        extracted_preferences = self._extract_preferences(user_input)
        updated_memory = self._merge_preferences(history, extracted_preferences, user_input)
        self.memory_repository.save_user_memory(self.user_id, updated_memory)

        result = {
            "user_id": self.user_id,
            "preferred_imagery": updated_memory["preferred_imagery"],
            "preferred_emotion_styles": updated_memory["preferred_emotion_styles"],
            "recent_inputs": updated_memory["recent_inputs"],
            "new_preferences": extracted_preferences,
            "source": "memory_json",
        }
        self.update_blackboard(result)
        return result

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        self._update_owned_field(data)

    def _extract_preferences(self, user_input: str) -> dict[str, list[str]]:
        """Extract user preferences from the current input."""
        text = user_input.strip()
        if not any(hint in text for hint in self._PREFERENCE_HINTS):
            return {
                "preferred_imagery": [],
                "preferred_emotion_styles": [],
            }

        preferred_imagery = [
            item for item in self._IMAGERY_OPTIONS if item in text
        ]
        preferred_emotion_styles = [
            item for item in self._EMOTION_STYLE_OPTIONS if item in text
        ]

        return {
            "preferred_imagery": preferred_imagery,
            "preferred_emotion_styles": preferred_emotion_styles,
        }

    def _merge_preferences(
        self,
        history: dict[str, Any],
        extracted_preferences: dict[str, list[str]],
        user_input: str,
    ) -> dict[str, Any]:
        """Merge current preference signals into stored memory."""
        preferred_imagery = self._merge_unique_list(
            history.get("preferred_imagery", []),
            extracted_preferences.get("preferred_imagery", []),
        )
        preferred_emotion_styles = self._merge_unique_list(
            history.get("preferred_emotion_styles", []),
            extracted_preferences.get("preferred_emotion_styles", []),
        )
        recent_inputs = self._build_recent_inputs(
            history.get("recent_inputs", []),
            user_input,
        )

        return {
            "preferred_imagery": preferred_imagery,
            "preferred_emotion_styles": preferred_emotion_styles,
            "recent_inputs": recent_inputs,
        }

    def _merge_unique_list(
        self, base_items: list[str], new_items: list[str]
    ) -> list[str]:
        """Keep preference values unique and ordered."""
        merged_items: list[str] = []
        for item in base_items + new_items:
            if item and item not in merged_items:
                merged_items.append(item)
        return merged_items

    def _build_recent_inputs(
        self, recent_inputs: list[str], user_input: str, max_count: int = 5
    ) -> list[str]:
        """Keep a short recent input history for later extension."""
        cleaned_input = user_input.strip()
        if not cleaned_input:
            return recent_inputs[:max_count]

        updated_inputs = [item for item in recent_inputs if item != cleaned_input]
        updated_inputs.append(cleaned_input)
        return updated_inputs[-max_count:]
