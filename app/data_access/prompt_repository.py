"""Prompt repository."""

from __future__ import annotations

from pathlib import Path


class PromptRepository:
    """Load prompt templates from the local prompts directory."""

    def __init__(self, prompt_dir: Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.prompt_dir = prompt_dir or project_root / "app" / "prompts"

    def load_prompt(self, filename: str) -> str:
        """Load one prompt template file."""
        prompt_path = self.prompt_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8").strip()
