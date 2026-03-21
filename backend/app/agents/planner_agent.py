from __future__ import annotations

from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.schemas import AgentResult


PLANNER_TASK = """
Decide which specialized security agents should run for the given file.
Return booleans only for these flags: run_injection, run_secrets, run_auth, run_dependency.
Consider file name, extension, and content hints.
Do NOT perform vulnerability analysis here—only planning.
If a flag is false, omit or set false explicitly. Keep logs brief.
"""


class PlannerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Planner Agent",
            system_instructions=(
                "You are a lightweight planner. Output strictly valid JSON matching the schema. "
                "No prose, no markdown."
            ),
        )

    def analyze(self, content: str, file_path: Optional[str] = None) -> AgentResult:
        # Reuse AgentResult schema; encode booleans in findings for now to keep consistency.
        extra = f"File: {file_path}\n" if file_path else ""
        instructions = (
            f"{extra}Return a single finding with title 'Planning' and description containing the flags. "
            "Use severity 'Info', line 0. Put flags in description as JSON."
        )
        result = self.run(code_snippet=content, task=PLANNER_TASK, instructions=instructions)
        result.agent = "Planner Agent"
        if not result.logs:
            result.logs = [f"[Planner] Analyzed {file_path or 'snippet'}"]
        return result
