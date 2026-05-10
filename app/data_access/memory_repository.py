"""Memory repository for user preference persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MemoryRepository:
    """Read and write user preference data in JSON format."""

    def __init__(self, memory_path: Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.memory_path = memory_path or project_root / "data" / "memory" / "memory.json"
        self._ensure_file()

    def load_all(self) -> dict[str, Any]:
        """Load the whole memory file."""
        if not self.memory_path.exists():
            return {"users": {}}

        data = json.loads(self.memory_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"users": {}}
        if "users" not in data or not isinstance(data["users"], dict):
            return {"users": {}}
        return data

    def get_user_memory(self, user_id: str) -> dict[str, Any]:
        """Load one user's memory record."""
        data = self.load_all()
        users = data.get("users", {})
        if user_id not in users:
            return self._default_user_memory()
        user_memory = users[user_id]
        if not isinstance(user_memory, dict):
            return self._default_user_memory()
        return {
            "preferred_imagery": list(user_memory.get("preferred_imagery", [])),
            "preferred_emotion_styles": list(
                user_memory.get("preferred_emotion_styles", [])
            ),
            "recent_inputs": list(user_memory.get("recent_inputs", [])),
        }

    def save_user_memory(self, user_id: str, user_memory: dict[str, Any]) -> None:
        """Persist one user's memory record."""
        data = self.load_all()
        data["users"][user_id] = {
            "preferred_imagery": list(user_memory.get("preferred_imagery", [])),
            "preferred_emotion_styles": list(
                user_memory.get("preferred_emotion_styles", [])
            ),
            "recent_inputs": list(user_memory.get("recent_inputs", [])),
        }
        self.memory_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _ensure_file(self) -> None:
        """Create the memory file with a minimal initial structure."""
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        if self.memory_path.exists():
            return
        self.memory_path.write_text(
            json.dumps({"users": {}}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _default_user_memory(self) -> dict[str, Any]:
        return {
            "preferred_imagery": [],
            "preferred_emotion_styles": [],
            "recent_inputs": [],
        }
