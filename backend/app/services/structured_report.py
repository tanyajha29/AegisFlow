from __future__ import annotations

import json
import logging
from typing import Iterable, List

import httpx
from pydantic import ValidationError

from ..config import get_settings
from ..models.scan_model import Scan
from ..schemas.report_schema import (
    FullStructuredReportSchema,
    ReportFindingSchema,
    ReportInsightsSchema,
    ReportRiskScoreSchema,
    ReportSummarySchema,
)
from ..services.risk_engine import calculate_risk_score, risk_level

logger = logging.getLogger("dristi-scan")
settings = get_settings()

REQUIRED_JSON_FORMAT = """{
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
}"""

STRUCTURED_PROMPT = """Code:
{code}

Instructions:
Analyze the code for security vulnerabilities and return ONLY valid JSON in the exact schema provided.
Do not return markdown.
Do not return explanation outside JSON.
If there are no vulnerabilities, still return the full JSON structure with empty findings and appropriate summary values.

Required JSON format:
{json_format}
"""


def _severity_counts(vulnerabilities: Iterable) -> dict[str, int]:
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for vuln in vulnerabilities:
        severity = getattr(vuln, "severity", None)
        severity = severity or (vuln.get("severity") if isinstance(vuln, dict) else None)
        if severity in counts:
            counts[severity] += 1
    counts["total"] = sum(counts.values())
    return counts


def _overall_risk_label(score_0_100: float, counts: dict[str, int]) -> str:
    # Map existing risk scoring to required labels without the "Risk" suffix.
    derived = risk_level(score_0_100)
    if derived.endswith(" Risk"):
        derived = derived.replace(" Risk", "")
    if counts.get("Critical"):
        return "Critical"
    if counts.get("High"):
        return "High"
    return derived or "Low"


def _vulnerability_to_finding(vuln) -> ReportFindingSchema:
    name = getattr(vuln, "name", None) or (vuln.get("name") if isinstance(vuln, dict) else "Vulnerability")
    severity = getattr(vuln, "severity", None) or (vuln.get("severity") if isinstance(vuln, dict) else "Low")
    line = getattr(vuln, "line_number", None)
    if line is None and isinstance(vuln, dict):
        line = vuln.get("line_number") or vuln.get("line")
    line = int(line) if line else 0
    code_snippet = getattr(vuln, "code_snippet", None)
    if code_snippet is None and isinstance(vuln, dict):
        code_snippet = vuln.get("code_snippet") or vuln.get("code")
    description = getattr(vuln, "description", None) or (vuln.get("description") if isinstance(vuln, dict) else "")
    remediation = getattr(vuln, "remediation", None) or (vuln.get("remediation") if isinstance(vuln, dict) else "")
    attack_example = ""
    if isinstance(vuln, dict):
        attack_example = vuln.get("attack_example") or ""
    fix_code = ""
    if isinstance(vuln, dict):
        fix_code = vuln.get("fix_code") or ""
    return ReportFindingSchema(
        type=name or "Vulnerability",
        severity=severity or "Low",
        line=line,
        code=code_snippet or "",
        description=description or "",
        impact=description or "Impact not specified.",
        attack_example=attack_example,
        recommendation=remediation or "Apply secure coding best practices.",
        fix_code=fix_code,
    )


def _build_fallback_report(scan: Scan) -> FullStructuredReportSchema:
    vulnerabilities = list(scan.vulnerabilities or [])
    counts = _severity_counts(vulnerabilities)
    score_0_100 = float(getattr(scan, "risk_score", 0.0) or 0.0)
    if counts["total"] > 0 and score_0_100 == 0.0:
        severities = [getattr(v, "severity", None) or v.get("severity") for v in vulnerabilities]
        score_0_100 = float(calculate_risk_score(severities))
    overall_risk = _overall_risk_label(score_0_100, counts)
    risk_score_10 = round(min(10.0, max(0.0, score_0_100 / 10.0)), 2)
    findings = [ _vulnerability_to_finding(v) for v in vulnerabilities ]
    primary_issue = findings[0].type if findings else "No vulnerabilities detected"
    insights = ReportInsightsSchema(
        summary="AI insights unavailable; using deterministic fallback based on stored findings.",
        most_critical_issue=primary_issue,
        fix_priority="Address higher severity findings first (Critical -> High -> Medium -> Low).",
    )
    summary = ReportSummarySchema(
        total=counts["total"],
        critical=counts["Critical"],
        high=counts["High"],
        medium=counts["Medium"],
        low=counts["Low"],
        overall_risk=overall_risk,
    )
    risk = ReportRiskScoreSchema(
        score=risk_score_10,
        reason=(
            f"Calculated from {counts['total']} findings with distribution "
            f"C/H/M/L = {counts['Critical']}/{counts['High']}/{counts['Medium']}/{counts['Low']}."
        ),
    )
    return FullStructuredReportSchema(
        summary=summary,
        findings=findings,
        risk_score=risk,
        ai_insights=insights,
        secure_version="",
    )


def _safe_json_parse(text: str) -> dict:
    candidates: List[str] = [text]
    if "```" in text:
        for part in text.split("```"):
            part = part.strip()
            if not part:
                continue
            if part.lower().startswith("json"):
                part = part[4:].strip()
            candidates.append(part)
    if "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        candidates.append(text[start:end])

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            try:
                repaired = candidate.replace("'", '"')
                return json.loads(repaired)
            except Exception:
                continue
    raise ValueError("Unable to parse AI JSON output")


def _call_ai(code_context: str) -> str:
    ollama_url = str(settings.ollama_url).rstrip("/")
    payload = {
        "model": settings.ollama_model,
        "prompt": STRUCTURED_PROMPT.format(code=code_context, json_format=REQUIRED_JSON_FORMAT),
        "stream": False,
    }
    with httpx.Client(timeout=settings.ollama_timeout_seconds or 25) as client:
        response = client.post(f"{ollama_url}/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return (data.get("response") or data.get("output") or response.text).strip()


def _build_code_context(scan: Scan) -> str:
    parts = [
        f"File/Target: {getattr(scan, 'file_name', 'unknown')}",
        f"Risk Score: {getattr(scan, 'risk_score', 0)}",
        f"Findings count: {len(getattr(scan, 'vulnerabilities', []) or [])}",
    ]
    for vuln in list(getattr(scan, "vulnerabilities", []) or [])[:8]:
        snippet = getattr(vuln, "code_snippet", None) or ""
        parts.append(
            f"[{vuln.severity}] {vuln.name} (line {getattr(vuln, 'line_number', 'n/a')})\n{snippet}"
        )
    context = "\n\n".join(parts) or "No code or findings available."
    # keep prompt bounded for latency while preserving content structure
    return context if len(context) <= 8000 else context[:8000]


def _normalize_ai_report(
    ai_report: FullStructuredReportSchema, fallback: FullStructuredReportSchema, counts: dict[str, int], score_0_100: float
) -> FullStructuredReportSchema:
    ai_report.summary.total = counts["total"]
    ai_report.summary.critical = counts["Critical"]
    ai_report.summary.high = counts["High"]
    ai_report.summary.medium = counts["Medium"]
    ai_report.summary.low = counts["Low"]
    ai_report.summary.overall_risk = _overall_risk_label(score_0_100, counts)

    if not ai_report.findings:
        ai_report.findings = fallback.findings

    if not ai_report.risk_score:
        ai_report.risk_score = fallback.risk_score
    else:
        ai_report.risk_score.score = round(min(10.0, max(0.0, ai_report.risk_score.score)), 2)
        if not ai_report.risk_score.reason:
            ai_report.risk_score.reason = fallback.risk_score.reason

    if not ai_report.ai_insights.summary:
        ai_report.ai_insights.summary = fallback.ai_insights.summary
    if not ai_report.ai_insights.most_critical_issue:
        ai_report.ai_insights.most_critical_issue = fallback.ai_insights.most_critical_issue
    if not ai_report.ai_insights.fix_priority:
        ai_report.ai_insights.fix_priority = fallback.ai_insights.fix_priority

    if ai_report.secure_version is None:
        ai_report.secure_version = fallback.secure_version
    return ai_report


def build_structured_report(scan: Scan) -> FullStructuredReportSchema:
    fallback = _build_fallback_report(scan)
    counts = _severity_counts(scan.vulnerabilities or [])
    score_0_100 = float(getattr(scan, "risk_score", 0.0) or 0.0)
    if not getattr(settings, "ai_report_enabled", False):
        return fallback

    try:
        raw = _call_ai(_build_code_context(scan))
        parsed = _safe_json_parse(raw)
        ai_report = FullStructuredReportSchema.model_validate(parsed)
        return _normalize_ai_report(ai_report, fallback, counts, score_0_100)
    except (ValidationError, Exception) as exc:
        logger.warning("Structured AI report failed or invalid. Falling back to deterministic version: %s", exc)
        return fallback
