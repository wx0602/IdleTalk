"""Planner agent implementation."""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.data_access.corpus_repository import CorpusRepository
from app.scheduler.agent_scheduler import AgentScheduler


class PlannerAgent(BaseAgent):
    """Analyze user input and drive the main execution chain."""

    def __init__(
        self,
        blackboard,
        scheduler: AgentScheduler,
        corpus_repository: CorpusRepository | None = None,
    ) -> None:
        super().__init__(blackboard)
        self.scheduler = scheduler
        self.corpus_repository = corpus_repository or CorpusRepository()

    @property
    def agent_name(self) -> str:
        return "planner_agent"

    def run(self, user_input: str) -> dict[str, Any]:
        """Analyze input, build plan, and execute the full workflow."""
        intent = self._analyze_user_input(user_input)
        corpus_info = self.corpus_repository.get_corpus_stats()
        execution_plan = self._build_execution_plan(intent, corpus_info)
        execution_result = self._execute_plan(execution_plan, user_input)

        return {
            "user_input": user_input,
            "intent": intent,
            "corpus": corpus_info,
            "plan": execution_plan,
            "execution": execution_result,
            "final_response": execution_result.get("summary_agent", {}).get(
                "final_response", ""
            ),
        }

    def read_blackboard(self) -> dict[str, Any]:
        return self._read_all_context()

    def update_blackboard(self, data: dict[str, Any]) -> None:
        # Planner acts as the coordinator and does not own a blackboard field.
        _ = data

    def _analyze_user_input(self, user_input: str) -> dict[str, Any]:
        """Use simple rules to identify the main interaction goal."""
        text = user_input.strip()
        lowered = text.lower()

        emotion_keywords = ["难过", "失落", "孤独", "烦", "累", "焦虑", "伤心"]
        imagery_keywords = ["生活", "晚饭", "雨", "灯", "街", "花", "风", "院子", "回忆"]
        comfort_keywords = ["安慰", "陪陪我", "想聊聊", "心情", "治愈"]

        need_emotion = True
        need_persona = True
        need_imagery = any(word in text for word in imagery_keywords) or any(
            word in text for word in comfort_keywords
        )
        need_memory = True

        if not need_imagery:
            need_imagery = len(text) > 8 or "write" in lowered or "style" in lowered

        return {
            "input_length": len(text),
            "has_emotion_signal": any(word in text for word in emotion_keywords),
            "needs_emotion": need_emotion,
            "needs_persona": need_persona,
            "needs_imagery": need_imagery,
            "needs_memory": need_memory,
            "needs_style": True,
            "needs_summary": True,
        }

    def _build_execution_plan(
        self, intent: dict[str, Any], corpus_info: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Build a lightweight and extensible execution plan."""
        parallel_agents: list[str] = []

        if intent["needs_imagery"]:
            parallel_agents.append("imagery_agent")
        if intent["needs_memory"]:
            parallel_agents.append("memory_agent")

        plan = []

        if intent["needs_emotion"]:
            plan.append({"mode": "serial", "agents": ["emotion_agent"]})

        if intent["needs_persona"]:
            plan.append({"mode": "serial", "agents": ["persona_agent"]})

        if parallel_agents:
            plan.append({"mode": "parallel", "agents": parallel_agents})

        if intent["needs_style"]:
            plan.append({"mode": "serial", "agents": ["style_agent"]})

        if intent["needs_summary"]:
            plan.append({"mode": "serial", "agents": ["summary_agent"]})

        # Pass the corpus state to downstream logic through the plan metadata.
        for step in plan:
            step["use_corpus"] = corpus_info["ready"]
            step["corpus_dir"] = corpus_info["corpus_dir"]

        return plan

    def _execute_plan(
        self, execution_plan: list[dict[str, Any]], user_input: str
    ) -> dict[str, Any]:
        """Run the workflow according to the planned serial/parallel steps."""
        results: dict[str, Any] = {}

        for step in execution_plan:
            mode = step["mode"]
            agent_names = step["agents"]

            if mode == "serial":
                results.update(self.scheduler.run_serial(agent_names, user_input))
            elif mode == "parallel":
                results.update(self.scheduler.run_parallel(agent_names, user_input))
            else:
                raise ValueError(f"Unsupported execution mode: {mode}")

            self._sync_summary_agent(results)

        return results

    def _sync_summary_agent(self, results: dict[str, Any]) -> None:
        """Pass style and execution data to SummaryAgent when available."""
        summary_agent = self.scheduler.agents.get("summary_agent")
        if summary_agent is None:
            return

        if hasattr(summary_agent, "set_agent_results"):
            summary_agent.set_agent_results(results)

        if "style_agent" in results and hasattr(summary_agent, "set_style_result"):
            summary_agent.set_style_result(results["style_agent"])
