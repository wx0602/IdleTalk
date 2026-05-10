"""Style agent implementation."""

from __future__ import annotations

import json
from typing import Any

from app.agents.base_agent import BaseAgent
from app.data_access.corpus_repository import CorpusRepository
from app.data_access.prompt_repository import PromptRepository
from app.utils.api_client import DeepSeekAPIClient, DeepSeekAPIError


class StyleAgent(BaseAgent):
    """Integrate blackboard context and call DeepSeek for final wording."""

    def __init__(
        self,
        blackboard,
        api_client: DeepSeekAPIClient | None = None,
        prompt_repository: PromptRepository | None = None,
        corpus_repository: CorpusRepository | None = None,
    ) -> None:
        super().__init__(blackboard)
        self.api_client = api_client or DeepSeekAPIClient()
        self.prompt_repository = prompt_repository or PromptRepository()
        self.corpus_repository = corpus_repository or CorpusRepository()

    @property
    def agent_name(self) -> str:
        return "style_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        context = self.read_blackboard()
        reference_quotes = self._select_reference_quotes(context)
        system_prompt = self.prompt_repository.load_prompt("style.txt")
        user_prompt = self._build_user_prompt(user_input, context, reference_quotes)

        try:
            generated_text = self.api_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.85,
                max_tokens=300,
            )
            status = "success"
            source = "deepseek_api"
            error_message = ""
        except DeepSeekAPIError as exc:
            generated_text = self._build_fallback_text(context)
            status = "fallback"
            source = "local_fallback"
            error_message = str(exc)

        return {
            "input": user_input,
            "emotion": context.get("emotion", {}),
            "persona": context.get("persona", {}),
            "imagery": context.get("imagery", {}),
            "memory": context.get("memory", {}),
            "reference_quotes": [
                {"id": item.get("id", ""), "text": item.get("text", "")}
                for item in reference_quotes
            ],
            "draft": generated_text,
            "status": status,
            "source": source,
            "error": error_message,
        }

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        # StyleAgent integrates context and stays read-only here.
        _ = data

    def _select_reference_quotes(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Pick a few corpus samples as style references."""
        quotes = self.corpus_repository.load_structured_quotes()
        if not quotes:
            return []

        emotion_label = context.get("emotion", {}).get("label", "calm")
        persona = context.get("persona", {})
        imagery = context.get("imagery", {})

        preferred_style_tags = self._infer_style_tags(persona)
        preferred_imagery = set(imagery.get("selected_imagery", []))

        scored_quotes: list[tuple[int, dict[str, Any]]] = []
        for quote in quotes:
            score = 0

            if emotion_label in quote.get("emotion", []):
                score += 3

            if any(tag in quote.get("style_tags", []) for tag in preferred_style_tags):
                score += 2

            if any(item in quote.get("imagery", []) for item in preferred_imagery):
                score += 2

            if "生活" in quote.get("theme", []):
                score += 1

            if quote.get("text"):
                scored_quotes.append((score, quote))

        ranked_quotes = [
            quote
            for _, quote in sorted(scored_quotes, key=lambda item: item[0], reverse=True)
            if quote.get("text")
        ]
        return ranked_quotes[:3]

    def _infer_style_tags(self, persona: dict[str, Any]) -> list[str]:
        """Map persona guidance to corpus style tags."""
        tags = ["生活化"]

        tone = persona.get("tone", "")
        pace = persona.get("pace", "")
        core_traits = persona.get("core_traits", [])

        if "温和" in tone or "温和" in core_traits:
            tags.append("温润")
        if "克制" in core_traits:
            tags.append("节制")
        if "平静" in core_traits:
            tags.append("平实")
        if "短" in pace:
            tags.append("短句")
        if "留白" in pace or "停顿" in pace:
            tags.append("留白")

        return tags

    def _build_user_prompt(
        self,
        user_input: str,
        context: dict[str, Any],
        reference_quotes: list[dict[str, Any]],
    ) -> str:
        """Build the user prompt with structured blackboard context."""
        prompt_payload = {
            "user_input": user_input,
            "emotion": context.get("emotion", {}),
            "persona": context.get("persona", {}),
            "imagery": context.get("imagery", {}),
            "memory": context.get("memory", {}),
            "reference_quotes": [
                {
                    "id": quote.get("id", ""),
                    "text": quote.get("text", ""),
                    "style_tags": quote.get("style_tags", []),
                    "imagery": quote.get("imagery", []),
                }
                for quote in reference_quotes
            ],
            "writing_constraints": {
                "length": "80-160字",
                "style": ["短句", "留白", "温和", "烟火气", "生活感"],
                "avoid": ["说教", "喊口号", "过度煽情", "直接模仿原句"],
            },
        }
        return json.dumps(prompt_payload, ensure_ascii=False, indent=2)

    def _build_fallback_text(self, context: dict[str, Any]) -> str:
        """Keep the workflow runnable when the API is unavailable."""
        emotion = context.get("emotion", {}).get("label", "calm")
        imagery_items = context.get("imagery", {}).get("selected_imagery", [])
        tone = context.get("persona", {}).get("tone", "温和")

        imagery_hint = "、".join(imagery_items[:2]) if imagery_items else "日常小景"
        return (
            f"现在先用本地回退结果。情绪是{emotion}。"
            f"语气保持{tone}。可以围绕{imagery_hint}慢慢展开。"
        )
