from __future__ import annotations

from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.schemas import AgentResult


DEPENDENCY_TASK = """
Analyze ONLY dependency manifests for risky or vulnerable packages.
Supported files: requirements.txt, Pipfile, poetry.lock, package.json, package-lock.json, yarn.lock.
Identify outdated/vulnerable versions, known risky packages, or missing version pins.
Return strict JSON per schema with severity, remediation, and confidence. Provide concise logs.
Do NOT report non-dependency issues.
"""


class DependencyAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Dependency Agent",
            system_instructions=(
                "You are a software supply-chain reviewer. Output strictly valid JSON only. "
                "No prose, markdown, or code fences."
            ),
        )

    def analyze(self, content: str, file_path: Optional[str] = None) -> AgentResult:
        extra = f"File: {file_path}\n" if file_path else ""
        instructions = f"{extra}Focus only on dependency/version risks. If the file is not a manifest, return empty findings."
        result = self.run(code_snippet=content, task=DEPENDENCY_TASK, instructions=instructions)

        result.agent = "Dependency Agent"
        for finding in result.findings:
            if "Dependency Agent" not in finding.detected_by:
                finding.detected_by.append("Dependency Agent")
        if not result.logs:
            result.logs = [f"[Dependency] Analyzed {file_path or 'manifest'}"]
        return result
