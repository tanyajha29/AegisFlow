from __future__ import annotations

from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.schemas import AgentResult


INJECTION_TASK = """
Analyze the provided code ONLY for injection issues (SQL injection, command injection, XSS, template injection).
Return precise findings with severity, file, line (if present), remediation, and confidence.
If nothing is found, return an empty findings array. Always emit a short log of what was scanned.
"""


class InjectionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Injection Agent",
            system_instructions=(
                "You are an expert code security reviewer. "
                "You must output strictly valid JSON matching the provided schema. "
                "No prose, no Markdown, no code fences."
            ),
        )

    def analyze(self, code_snippet: str, file_path: Optional[str] = None) -> AgentResult:
        extra = ""
        if file_path:
            extra = f"File: {file_path}\n"
        instructions = f"{extra}Focus ONLY on injection categories: SQLi, command injection, XSS, template injection."
        result = self.run(code_snippet=code_snippet, task=INJECTION_TASK, instructions=instructions)

        # Ensure agent name and detected_by tagging
        result.agent = "Injection Agent"
        for finding in result.findings:
            if "Injection Agent" not in finding.detected_by:
                finding.detected_by.append("Injection Agent")
        if not result.logs:
            result.logs = [f"[Injection] Analyzed {file_path or 'snippet'}"]
        return result
