"""Summary agent implementation."""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent


class SummaryAgent(BaseAgent):
    """Aggregate agent results into a frontend-friendly response."""

    def __init__(self, blackboard) -> None:
        super().__init__(blackboard)
        self.style_result: dict[str, Any] = {}
        self.agent_results: dict[str, Any] = {}

    @property
    def agent_name(self) -> str:
        return "summary_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        context = self.read_blackboard()
        final_text = self.style_result.get("draft", "")
        if not final_text:
            final_text = self._build_fallback_response(context)

        emotion = context.get("emotion", {})
        persona = context.get("persona", {})
        imagery = context.get("imagery", {})
        memory = context.get("memory", {})

        return {
            "status": "success" if final_text else "empty",
            "user_input": user_input,
            "final_response": final_text,
            "display": {
                "text": final_text,
                "emotion": emotion.get("label", "calm"),
                "tone": persona.get("tone", ""),
                "imagery": imagery.get("selected_imagery", []),
            },
            "context": {
                "emotion": emotion,
                "persona": persona,
                "imagery": imagery,
                "memory": memory,
            },
            "trace": {
                "style_status": self.style_result.get("status", ""),
                "style_source": self.style_result.get("source", ""),
                "style_reference_quotes": self.style_result.get("reference_quotes", []),
                "memory_preferences": {
                    "preferred_imagery": memory.get("preferred_imagery", []),
                    "preferred_emotion_styles": memory.get(
                        "preferred_emotion_styles", []
                    ),
                },
                "agent_names": sorted(self.agent_results.keys()),
            },
        }

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        # SummaryAgent only packages results in this simplified design.
        _ = data

    def set_style_result(self, style_result: dict[str, Any]) -> None:
        """Inject Style Agent output before summary packaging."""
        self.style_result = style_result

    def set_agent_results(self, agent_results: dict[str, Any]) -> None:
        """Keep a lightweight execution trace for frontend display."""
        self.agent_results = agent_results

    def _build_fallback_response(self, context: dict[str, Any]) -> str:
        """Fallback final response if style output is missing."""
        emotion = context.get("emotion", {}).get("label", "calm")
        tone = context.get("persona", {}).get("tone", "温和")
        imagery = context.get("imagery", {}).get("selected_imagery", [])

        imagery_hint = "、".join(imagery[:2]) if imagery else "日常小景"
        return f"情绪识别为{emotion}，建议用{tone}的语气，围绕{imagery_hint}展开表达。"
