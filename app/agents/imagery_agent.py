"""Imagery agent implementation."""

from __future__ import annotations

import random
from typing import Any

from app.agents.base_agent import BaseAgent
from app.data_access.corpus_repository import CorpusRepository


class ImageryAgent(BaseAgent):
    """Generate everyday-life imagery from the structured corpus."""

    def __init__(
        self,
        blackboard,
        corpus_repository: CorpusRepository | None = None,
    ) -> None:
        super().__init__(blackboard)
        self.corpus_repository = corpus_repository or CorpusRepository()

    @property
    def agent_name(self) -> str:
        return "imagery_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        _ = user_input
        emotion_state = self._read_context_field("emotion")
        persona_state = self._read_context_field("persona")
        quotes = self.corpus_repository.load_structured_quotes()

        selected_quotes = self._select_quotes(quotes, emotion_state, persona_state)
        result = self._build_result(selected_quotes, emotion_state, persona_state)
        self.update_blackboard(result)
        return result

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        self._update_owned_field(data)

    def _select_quotes(
        self,
        quotes: list[dict[str, Any]],
        emotion_state: dict[str, Any],
        persona_state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Select quote cards whose tags fit the current state."""
        if not quotes:
            return []

        emotion_label = emotion_state.get("label", "calm")
        persona_traits = persona_state.get("core_traits", [])
        persona_focus = persona_state.get("focus", "")
        preferred_style_tags = self._infer_style_tags(persona_traits, persona_focus)

        scored_quotes: list[tuple[int, dict[str, Any]]] = []
        for quote in quotes:
            score = 0

            if emotion_label in quote.get("emotion", []):
                score += 3

            if quote.get("imagery"):
                score += 2

            if quote.get("scene"):
                score += 1

            if "生活" in quote.get("theme", []):
                score += 1

            score += sum(1 for tag in preferred_style_tags if tag in quote.get("style_tags", []))

            scored_quotes.append((score, quote))

        matched_quotes = [quote for score, quote in scored_quotes if score >= 3]
        if len(matched_quotes) < 3:
            matched_quotes = [
                quote
                for _, quote in sorted(scored_quotes, key=lambda item: item[0], reverse=True)
                if quote.get("imagery") or quote.get("scene")
            ]

        pick_count = min(3, len(matched_quotes))
        if pick_count == 0:
            return []

        return random.sample(matched_quotes, k=pick_count)

    def _build_result(
        self,
        selected_quotes: list[dict[str, Any]],
        emotion_state: dict[str, Any],
        persona_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Build structured imagery output for downstream agents."""
        if not selected_quotes:
            return {
                "emotion_reference": emotion_state.get("label", "calm"),
                "persona_reference": persona_state.get("tone", "平和自然"),
                "selected_imagery": [],
                "selected_scenes": [],
                "quote_refs": [],
                "supporting_texts": [],
                "scene_hint": "用普通日常小景承接情绪",
                "life_breath": "清淡、安静的烟火气",
                "source": "corpus_json",
            }

        imagery_pool = self._collect_unique_values(selected_quotes, "imagery")
        scene_pool = self._collect_unique_values(selected_quotes, "scene")
        quote_refs = [quote.get("id", "") for quote in selected_quotes if quote.get("id")]
        supporting_texts = [quote.get("text", "") for quote in selected_quotes if quote.get("text")]

        selected_imagery = self._pick_values(imagery_pool, 4)
        selected_scenes = self._pick_values(scene_pool, 2)
        scene_hint = "，".join(selected_imagery or selected_scenes)
        atmosphere = self._build_life_breath(selected_quotes)

        return {
            "emotion_reference": emotion_state.get("label", "calm"),
            "persona_reference": persona_state.get("tone", "平和自然"),
            "selected_imagery": selected_imagery,
            "selected_scenes": selected_scenes,
            "quote_refs": quote_refs,
            "supporting_texts": supporting_texts,
            "scene_hint": f"可围绕{scene_hint}展开生活化描写",
            "life_breath": atmosphere,
            "source": "corpus_json",
        }

    def _infer_style_tags(self, traits: list[str], focus: str) -> list[str]:
        """Map persona features to corpus style tags."""
        inferred_tags = []
        if "温和" in traits:
            inferred_tags.append("温润")
        if "克制" in traits:
            inferred_tags.append("节制")
        if "平静" in traits:
            inferred_tags.append("平实")
        if "生活" in focus:
            inferred_tags.append("白描")
        return inferred_tags

    def _collect_unique_values(
        self, quotes: list[dict[str, Any]], field_name: str
    ) -> list[str]:
        """Collect unique tag values from selected quote cards."""
        values: list[str] = []
        for quote in quotes:
            field_value = quote.get(field_name, [])
            if not isinstance(field_value, list):
                continue
            for item in field_value:
                if isinstance(item, str) and item and item not in values:
                    values.append(item)
        return values

    def _pick_values(self, values: list[str], max_count: int) -> list[str]:
        """Randomly pick a few values while keeping the result compact."""
        if not values:
            return []
        if len(values) <= max_count:
            return values
        return random.sample(values, k=max_count)

    def _build_life_breath(self, selected_quotes: list[dict[str, Any]]) -> str:
        """Summarize the atmosphere from quote tags instead of a base imagery file."""
        theme_pool = self._collect_unique_values(selected_quotes, "theme")
        scene_pool = self._collect_unique_values(selected_quotes, "scene")

        if "生活" in theme_pool and scene_pool:
            return "带着日常起居和具体场景的烟火气"
        if scene_pool:
            return "有场景感、能落到日常细节里的生活气息"
        return "清淡平实的生活感"
