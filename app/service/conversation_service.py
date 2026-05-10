"""Conversation orchestration service."""

from __future__ import annotations

from app.agents.emotion_agent import EmotionAgent
from app.agents.imagery_agent import ImageryAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.persona_agent import PersonaAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.style_agent import StyleAgent
from app.agents.summary_agent import SummaryAgent
from app.blackboard.blackboard import Blackboard
from app.scheduler.agent_scheduler import AgentScheduler


class ConversationService:
    """Create and run one complete multi-agent workflow."""

    def run_chat(self, user_input: str, user_id: str = "default_user") -> dict:
        """Run the planner-led workflow and return the final summary."""
        blackboard = Blackboard()
        agents = self._build_agents(blackboard, user_id)
        scheduler = AgentScheduler(agents)
        planner = PlannerAgent(blackboard=blackboard, scheduler=scheduler)

        planner_result = planner.run(user_input)
        return planner_result.get("execution", {}).get(
            "summary_agent",
            {
                "status": "error",
                "user_input": user_input,
                "final_response": "",
                "display": {"text": "", "emotion": "", "tone": "", "imagery": []},
                "context": {},
                "trace": {"message": "summary_agent did not return a result"},
            },
        )

    def _build_agents(self, blackboard: Blackboard, user_id: str) -> dict:
        """Build agent instances for one request."""
        return {
            "emotion_agent": EmotionAgent(blackboard),
            "persona_agent": PersonaAgent(blackboard),
            "imagery_agent": ImageryAgent(blackboard),
            "memory_agent": MemoryAgent(blackboard, user_id=user_id),
            "style_agent": StyleAgent(blackboard),
            "summary_agent": SummaryAgent(blackboard),
        }
