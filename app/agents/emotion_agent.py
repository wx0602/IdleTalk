"""Emotion agent implementation."""

from __future__ import annotations

import re
from typing import Any

from app.agents.base_agent import BaseAgent


class EmotionAgent(BaseAgent):
    """Analyze user emotion with simple rules and store the result."""

    _EMOTION_KEYWORDS = {
        "sad": [
            "难过",
            "伤心",
            "失落",
            "沮丧",
            "委屈",
            "不开心",
            "低落",
            "想哭",
        ],
        "lonely": [
            "孤独",
            "孤单",
            "一个人",
            "没人懂",
            "寂寞",
            "冷清",
            "没有人陪",
        ],
        "anxious": [
            "焦虑",
            "紧张",
            "害怕",
            "担心",
            "不安",
            "压力大",
            "烦",
            "慌",
        ],
        "calm": [
            "平静",
            "安静",
            "还好",
            "慢慢来",
            "放松",
            "没事",
            "稳定",
        ],
        "nostalgic": [
            "怀念",
            "想起",
            "以前",
            "从前",
            "小时候",
            "记得",
            "老街",
            "故乡",
            "过去",
        ],
    }

    @property
    def agent_name(self) -> str:
        return "emotion_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        # Emotion recognition is independent and does not need the corpus for now.
        _ = self.read_blackboard()
        result = self._detect_emotion(user_input)
        self.update_blackboard(result)
        return result

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        self._update_owned_field(data)

    def _detect_emotion(self, user_input: str) -> dict[str, Any]:
        """Rule-based emotion recognition.

        This method can be replaced later by a DeepSeek API implementation
        without changing the external agent interface.
        """
        text = user_input.strip()
        scores = {emotion: 0 for emotion in self._EMOTION_KEYWORDS}
        evidence: dict[str, list[str]] = {emotion: [] for emotion in self._EMOTION_KEYWORDS}

        for emotion, keywords in self._EMOTION_KEYWORDS.items():
            for keyword in keywords:
                match_count = text.count(keyword)
                if match_count > 0:
                    scores[emotion] += match_count
                    evidence[emotion].append(keyword)

        if not text:
            return self._build_result(
                label="calm",
                score=0,
                total_score=0,
                evidence=[],
                user_input=text,
            )

        label = max(scores, key=scores.get)
        total_score = sum(scores.values())

        if total_score == 0:
            label = self._fallback_emotion(text)

        return self._build_result(
            label=label,
            score=scores.get(label, 0),
            total_score=total_score,
            evidence=evidence.get(label, []),
            user_input=text,
        )

    def _fallback_emotion(self, text: str) -> str:
        """Fallback when no explicit keywords are matched."""
        if "？" in text or "?" in text:
            return "anxious"
        if re.search(r"(以前|从前|那时候|曾经|记得)", text):
            return "nostalgic"
        if re.search(r"(一个人|深夜|晚上)", text):
            return "lonely"
        return "calm"

    def _build_result(
        self,
        label: str,
        score: int,
        total_score: int,
        evidence: list[str],
        user_input: str,
    ) -> dict[str, Any]:
        """Build a unified output structure."""
        intensity = self._calculate_intensity(score, total_score, user_input)
        confidence = self._calculate_confidence(score, total_score)

        return {
            "label": label,
            "intensity": intensity,
            "confidence": confidence,
            "evidence": evidence,
            "source": "rule_based",
        }

    def _calculate_intensity(self, score: int, total_score: int, text: str) -> float:
        """Estimate emotion intensity with a simple score."""
        exclamation_bonus = text.count("！") + text.count("!")
        repeated_char_bonus = 1 if re.search(r"(太|很|特别).{0,3}(难|烦|怕|想)", text) else 0

        raw_score = score + exclamation_bonus + repeated_char_bonus
        if total_score == 0:
            raw_score = max(raw_score, 1)

        intensity = min(1.0, 0.3 + raw_score * 0.15)
        return round(intensity, 2)

    def _calculate_confidence(self, score: int, total_score: int) -> float:
        """Estimate label confidence based on keyword match strength."""
        if total_score == 0:
            return 0.4

        confidence = score / total_score
        return round(max(0.4, min(1.0, confidence)), 2)
