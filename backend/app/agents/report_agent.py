from __future__ import annotations

from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.schemas import AgentResult
from app.schemas.report_schema import Report


REPORT_TASK = """
You are a security report writer. Produce:
- Executive summary (2-4 sentences, business friendly)
- Key remediation themes (3-5 bullets)
- Optional grouped finding highlights (1-3 bullets)
Return strict JSON per provided schema; each item goes into findings:
  - title: section title (e.g., "Executive Summary", "Remediation Recommendations")
  - severity: use "Info"
  - description: the content (bullets allowed with newline-separated "- ")
  - remediation: short next steps for that section
  - confidence: 0.6-0.95
If no content, return empty findings. Always include concise logs.
"""


def _report_to_context(report: Report) -> str:
    parts = [
        f"File/Target: {report.file_name}",
        f"Risk Score: {report.risk_score}",
        f"Security Score: {report.security_score}",
        f"Findings: total={report.total_vulnerabilities}, "
        f"C/H/M/L = {report.critical_count}/{report.high_count}/{report.medium_count}/{report.low_count}",
        "Top findings:",
    ]
    for vuln in report.vulnerabilities[:5]:
        parts.append(
            f"- {vuln.severity}: {vuln.name} (file={vuln.file_name}, line={vuln.line_number}) "
            f"remediation={vuln.remediation}"
        )
    return "\n".join(parts)


class ReportAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Report Agent",
            system_instructions=(
                "You generate concise, structured security report sections. "
                "Output strictly valid JSON per schema; no prose outside JSON."
            ),
        )

    def analyze(self, report: Report) -> AgentResult:
        context = _report_to_context(report)
        instructions = "Base your summary on the provided scan context. Keep it crisp."
        result = self.run(code_snippet=context, task=REPORT_TASK, instructions=instructions)

        result.agent = "Report Agent"
        for finding in result.findings:
            if "Report Agent" not in finding.detected_by:
                finding.detected_by.append("Report Agent")
            finding.severity = "Info"
        if not result.logs:
            result.logs = ["[Report] Generated report sections."]
        return result
