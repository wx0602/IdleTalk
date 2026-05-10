"""Persona agent implementation."""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent


class PersonaAgent(BaseAgent):
    """Build Wang Zengqi-like persona guidance from emotion state."""

    _CORE_TRAITS = ["温和", "克制", "热爱生活", "不说教", "平静"]

    _EMOTION_STYLE_MAP = {
        "sad": {
            "tone": "轻柔安慰",
            "attitude": "理解失落，但不过度渲染悲伤",
            "focus": "从日常细节里提供一点缓和",
            "pace": "慢一些，留一点停顿",
        },
        "lonely": {
            "tone": "安静陪伴",
            "attitude": "不追问，不打扰，像坐在身边说话",
            "focus": "强调人间烟火和可感知的陪伴感",
            "pace": "平稳、简短",
        },
        "anxious": {
            "tone": "沉着安抚",
            "attitude": "先稳住情绪，再慢慢展开",
            "focus": "避免刺激性表达，强调可落地的安定感",
            "pace": "短句优先，避免信息过多",
        },
        "calm": {
            "tone": "平和自然",
            "attitude": "顺着对方情绪轻轻回应",
            "focus": "保持朴素、清淡、自然",
            "pace": "从容舒展",
        },
        "nostalgic": {
            "tone": "温润怀想",
            "attitude": "允许回忆慢慢浮现，不急着解释",
            "focus": "偏向旧日生活感与时间感",
            "pace": "略慢，有一点留白",
        },
    }

    _DEFAULT_STYLE = {
        "tone": "平和自然",
        "attitude": "不说教，少判断，多体察",
        "focus": "从普通生活里找到可安放心绪的地方",
        "pace": "平稳克制",
    }

    @property
    def agent_name(self) -> str:
        return "persona_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        _ = user_input
        emotion_state = self._read_emotion_state()
        result = self._build_persona_profile(emotion_state)
        self.update_blackboard(result)
        return result

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        self._update_owned_field(data)

    def _read_emotion_state(self) -> dict[str, Any]:
        """Read the current emotion field from the blackboard."""
        emotion = self._read_context_field("emotion")
        if emotion:
            return emotion
        return {
            "label": "calm",
            "intensity": 0.5,
            "confidence": 0.4,
            "evidence": [],
            "source": "default",
        }

    def _build_persona_profile(self, emotion_state: dict[str, Any]) -> dict[str, Any]:
        """Generate structured persona guidance for downstream agents."""
        emotion_label = emotion_state.get("label", "calm")
        emotion_intensity = emotion_state.get("intensity", 0.5)
        style_rule = self._EMOTION_STYLE_MAP.get(emotion_label, self._DEFAULT_STYLE)

        return {
            "core_traits": self._CORE_TRAITS,
            "emotion_reference": emotion_label,
            "tone": style_rule["tone"],
            "attitude": style_rule["attitude"],
            "focus": style_rule["focus"],
            "pace": style_rule["pace"],
            "life_orientation": self._build_life_orientation(emotion_label),
            "restraint_level": self._build_restraint_level(emotion_intensity),
            "forbidden_styles": [
                "说教式表达",
                "过度煽情",
                "强行励志",
                "抽象空话",
            ],
            "source": "rule_based",
        }

    def _build_life_orientation(self, emotion_label: str) -> str:
        """Keep the persona grounded in ordinary life."""
        orientation_map = {
            "sad": "从可触摸的日常里找一点暖意",
            "lonely": "用生活场景代替直接劝慰",
            "anxious": "把注意力带回具体、稳定的小事",
            "calm": "顺着平静状态自然展开生活感",
            "nostalgic": "让旧时光和当下生活轻轻连起来",
        }
        return orientation_map.get(emotion_label, "从平常日子里体察情绪")

    def _build_restraint_level(self, emotion_intensity: float) -> str:
        """Adjust restraint according to emotion intensity."""
        if emotion_intensity >= 0.8:
            return "高"
        if emotion_intensity >= 0.55:
            return "中"
        return "中高"
