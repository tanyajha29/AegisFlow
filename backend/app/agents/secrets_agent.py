from __future__ import annotations

from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.schemas import AgentResult


SECRETS_TASK = """
Analyze the provided content ONLY for exposed secrets and credentials:
- API keys (AWS, GCP, Azure, Stripe, GitHub, etc.)
- Hardcoded passwords
- Private keys / certificates
- Tokens (JWT, bearer tokens, PATs)
For each secret, provide title, severity, file, line (if available), remediation, and confidence.
Return strictly valid JSON per schema; if nothing is found, return an empty findings array.
Include concise log lines of your actions.
"""


class SecretsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Secrets Agent",
            system_instructions=(
                "You are a secrets-detection specialist. Output strictly valid JSON. "
                "No prose, no markdown, no code fences."
            ),
        )

    def analyze(self, content: str, file_path: Optional[str] = None) -> AgentResult:
        extra = f"File: {file_path}\n" if file_path else ""
        instructions = (
            f"{extra}Focus ONLY on secrets/credentials. Ignore non-secret issues such as injection or auth logic."
        )
        result = self.run(code_snippet=content, task=SECRETS_TASK, instructions=instructions)

        result.agent = "Secrets Agent"
        for finding in result.findings:
            if "Secrets Agent" not in finding.detected_by:
                finding.detected_by.append("Secrets Agent")
        if not result.logs:
            result.logs = [f"[Secrets] Analyzed {file_path or 'snippet'}"]
        return result
