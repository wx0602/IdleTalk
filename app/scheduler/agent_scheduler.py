"""Lightweight scheduler for agent execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from app.agents.base_agent import BaseAgent


class AgentScheduler:
    """Run agents in serial or parallel with simple Python logic."""

    def __init__(self, agents: dict[str, BaseAgent]) -> None:
        self.agents = agents

    def run_serial(self, agent_names: list[str], user_input: str) -> dict[str, Any]:
        """Run agents one by one in the given order."""
        results: dict[str, Any] = {}
        for agent_name in agent_names:
            agent = self._get_agent(agent_name)
            results[agent_name] = agent.run(user_input)
        return results

    def run_parallel(self, agent_names: list[str], user_input: str) -> dict[str, Any]:
        """Run independent agents in parallel."""
        if not agent_names:
            return {}

        results: dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=len(agent_names)) as executor:
            future_to_name = {
                executor.submit(self._get_agent(agent_name).run, user_input): agent_name
                for agent_name in agent_names
            }
            for future in as_completed(future_to_name):
                agent_name = future_to_name[future]
                results[agent_name] = future.result()
        return results

    def _get_agent(self, agent_name: str) -> BaseAgent:
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' is not registered.")
        return self.agents[agent_name]
