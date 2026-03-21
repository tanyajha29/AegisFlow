import logging
import textwrap
from typing import Optional

import httpx

from ..config import get_settings
from ..schemas.report_schema import Report
from app.agents.orchestrator import run_report_agent_if_enabled

logger = logging.getLogger("dristi-scan")
settings = get_settings()

DEFAULT_PROMPT = """You are a senior application security engineer.
Given the following scan facts, write a concise executive insight (4-6 sentences) plus 3 prioritized remediation bullets.
Facts:
- File: {file_name}
- Risk score: {risk_score}
- Total findings: {total}
- Severity counts: Critical={critical}, High={high}, Medium={medium}, Low={low}
- Top findings:
{top_findings}
Keep language business-friendly, include urgency if critical/high exist, and avoid code blocks.
"""


def _format_top_findings(report: Report, limit: int = 5) -> str:
    lines = []
    for vuln in report.vulnerabilities[:limit]:
        lines.append(f"- {vuln.severity}: {vuln.name} (file={vuln.file_name}, line={vuln.line_number})")
    return "\n".join(lines) or "- No specific findings provided."


def _report_agent_insight(report: Report) -> Optional[str]:
    res = run_report_agent_if_enabled(report)
    if not res or not res.findings:
        return None
    parts = []
    for f in res.findings:
        parts.append(f"{f.title}: {f.description}")
        if f.remediation:
            parts.append(f"Remediation: {f.remediation}")
    return textwrap.shorten("\n".join(parts), width=1200, placeholder=" …")


def generate_ai_insight(report: Report) -> Optional[str]:
    """
    Return a short AI-generated executive insight.
    Prefers structured Report Agent; falls back to legacy Ollama prompt if disabled/unavailable.
    """
    try:
        ai_summary = _report_agent_insight(report)
        if ai_summary:
            return ai_summary
    except Exception as exc:
        logger.warning("Report Agent insight failed, falling back: %s", exc)

    ollama_url = str(settings.ollama_url).rstrip("/")
    payload = {
        "model": settings.ollama_model,
        "prompt": DEFAULT_PROMPT.format(
            file_name=report.file_name,
            risk_score=report.risk_score,
            total=report.total_vulnerabilities,
            critical=report.critical_count or 0,
            high=report.high_count or 0,
            medium=report.medium_count or 0,
            low=report.low_count or 0,
            top_findings=_format_top_findings(report),
        ),
        "stream": False,
    }
    try:
        with httpx.Client(timeout=settings.ollama_timeout_seconds or 25) as client:
            resp = client.post(f"{ollama_url}/api/generate", json=payload)
            resp.raise_for_status()
            text = resp.json().get("response") or resp.text
            return textwrap.shorten(text.strip(), width=1200, placeholder=" …")
    except Exception as exc:  # pragma: no cover - best-effort
        logger.warning("AI insight generation failed: %s", exc)
        return None
