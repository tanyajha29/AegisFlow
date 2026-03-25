from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

SCHEMA_EXAMPLE = """
{
  "summary": {
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "overall_risk": "Low"
  },
  "findings": [
    {
      "type": "",
      "severity": "",
      "line": 0,
      "code": "",
      "description": "",
      "impact": "",
      "attack_example": "",
      "recommendation": "",
      "fix_code": ""
    }
  ],
  "risk_score": {
    "score": 0,
    "reason": ""
  },
  "ai_insights": {
    "summary": "",
    "most_critical_issue": "",
    "fix_priority": ""
  },
  "secure_version": ""
}
""".strip()


def _safe_str(value: Any, fallback: str = "") -> str:
    return str(value).strip() if value not in (None, "") else fallback


class ReportAgent(BaseAgent):
    """
    Generates structured explanatory content for scan findings.
    """

    def build_prompt(
        self,
        findings: List[Dict[str, Any]],
        summary: Dict[str, Any],
        risk_score_10: float,
        code: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> str:
        file_hint = file_name or "the scanned target"
        findings_json = json.dumps(findings, ensure_ascii=False, indent=2)
        summary_json = json.dumps(summary, ensure_ascii=False, indent=2)
        return (
            "You are a security report writer.\n"
            "Use ONLY the provided findings and context. Do NOT invent new vulnerabilities.\n"
            "Return ONLY valid JSON. No markdown. No text outside JSON.\n"
            "Use exactly this schema:\n"
            f"{SCHEMA_EXAMPLE}\n"
            "Rules:\n"
            "- Keep language professional and precise.\n"
            "- If there are no findings, return the full JSON with findings: [] and appropriate summary values.\n"
            "- Provide impact, attack_example, recommendation, and fix_code for each finding using the supplied context.\n"
            f"File: {file_hint}\n"
            f"Risk score (0-10): {risk_score_10}\n"
            "Summary counts:\n"
            f"{summary_json}\n"
            "Findings:\n"
            f"{findings_json}\n"
            f"Code (optional):\n{code or 'No code provided.'}\n"
            "Respond now with JSON only."
        )

    def _normalize(self, data: Any, summary_defaults: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure the output strictly follows the schema and fill safe defaults.
        """
        if not isinstance(data, dict):
            return {}

        summary_input = data.get("summary", {}) or {}
        findings_input = data.get("findings", []) or []
        risk_input = data.get("risk_score", {}) or {}
        insights_input = data.get("ai_insights", {}) or {}
        secure_version = _safe_str(data.get("secure_version"), "")

        summary = {
            "total": int(summary_input.get("total", summary_defaults["total"])),
            "critical": int(summary_input.get("critical", summary_defaults["critical"])),
            "high": int(summary_input.get("high", summary_defaults["high"])),
            "medium": int(summary_input.get("medium", summary_defaults["medium"])),
            "low": int(summary_input.get("low", summary_defaults["low"])),
            "overall_risk": _safe_str(summary_input.get("overall_risk"), summary_defaults["overall_risk"]),
        }

        normalized_findings: List[Dict[str, Any]] = []
        if isinstance(findings_input, list):
            for item in findings_input:
                if not isinstance(item, dict):
                    continue
                normalized_findings.append(
                    {
                        "type": _safe_str(item.get("type"), "Vulnerability"),
                        "severity": _safe_str(item.get("severity"), "Medium"),
                        "line": int(item.get("line", 0) or 0),
                        "code": _safe_str(item.get("code"), ""),
                        "description": _safe_str(item.get("description"), ""),
                        "impact": _safe_str(item.get("impact"), "Impact not provided."),
                        "attack_example": _safe_str(item.get("attack_example"), "Attack example not provided."),
                        "recommendation": _safe_str(
                            item.get("recommendation"), "Apply secure coding best practices."
                        ),
                        "fix_code": _safe_str(item.get("fix_code"), ""),
                    }
                )

        risk_score = float(risk_input.get("score", 0) or 0.0)
        risk_score = max(0.0, min(10.0, risk_score))
        risk_reason = _safe_str(risk_input.get("reason"), "Risk scored based on supplied findings.")

        ai_insights = {
            "summary": _safe_str(insights_input.get("summary"), ""),
            "most_critical_issue": _safe_str(insights_input.get("most_critical_issue"), ""),
            "fix_priority": _safe_str(insights_input.get("fix_priority"), ""),
        }

        return {
            "summary": summary,
            "findings": normalized_findings,
            "risk_score": {"score": risk_score, "reason": risk_reason},
            "ai_insights": ai_insights,
            "secure_version": secure_version,
        }

    def generate_report(
        self,
        findings: List[Dict[str, Any]],
        summary: Dict[str, Any],
        risk_score_10: float,
        code: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        prompt = self.build_prompt(findings=findings, summary=summary, risk_score_10=risk_score_10, code=code, file_name=file_name)
        raw = self.send_prompt(prompt)
        parsed = self.safe_json_loads(raw)
        if parsed is None:
            logger.warning("Report Agent returned non-JSON response; using fallback.")
            return None
        normalized = self._normalize(parsed, summary_defaults=summary)
        if not normalized:
            return None
        return normalized


def run_report_agent(
    findings: List[Dict[str, Any]],
    summary: Dict[str, Any],
    risk_score_10: float,
    code: Optional[str] = None,
    file_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    agent = ReportAgent()
    return agent.generate_report(
        findings=findings,
        summary=summary,
        risk_score_10=risk_score_10,
        code=code,
        file_name=file_name,
    )
