from __future__ import annotations

from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.schemas import AgentResult


AUTH_TASK = """
Analyze the provided code for authentication and authorization weaknesses ONLY:
- weak password checks or missing validation
- missing authorization checks / role checks / allow-all routes
- insecure JWT usage (hardcoded secrets, long-lived tokens, missing verification)
- hardcoded auth secrets or tokens
Return strict JSON per schema with severity, remediation, confidence. If no auth issues, return empty findings.
Include concise log lines. Do not report non-auth issues (e.g., SQLi, secrets unrelated to auth).
"""


class AuthAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Auth Agent",
            system_instructions=(
                "You are an authentication and authorization specialist. "
                "Output strictly valid JSON, no prose or markdown."
            ),
        )

    def analyze(self, content: str, file_path: Optional[str] = None) -> AgentResult:
        extra = f"File: {file_path}\n" if file_path else ""
        instructions = f"{extra}Focus only on auth/session/JWT/role/permission logic."
        result = self.run(code_snippet=content, task=AUTH_TASK, instructions=instructions)

        result.agent = "Auth Agent"
        for finding in result.findings:
            if "Auth Agent" not in finding.detected_by:
                finding.detected_by.append("Auth Agent")
        if not result.logs:
            result.logs = [f"[Auth] Analyzed {file_path or 'snippet'}"]
        return result
