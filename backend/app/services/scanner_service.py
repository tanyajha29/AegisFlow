from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

from ..scanner.orchestrator import run_pipeline_sync
from ..scanner.rule_engine import RuleEngineScanner
from .risk_engine import calculate_risk_score

_rule_engine = RuleEngineScanner()


def normalize_vulnerability(vuln: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "line_number": None,
        "description": "",
        "remediation": "Review and fix the issue.",
        "cwe_reference": None,
        "code_snippet": None,
        "category": vuln.get("category"),
    }
    normalized = {**defaults, **vuln}
    normalized["file_name"] = Path(vuln.get("file_name", "unknown.txt")).as_posix()
    normalized["severity"] = normalized.get("severity", "Medium")
    return normalized


def _summarize(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    severities = [f["severity"] for f in findings]
    counts = Counter(severities)
    risk_score = int(round(calculate_risk_score(severities) if findings else 0.0))
    security_score = int(round(max(0.0, 100.0 - risk_score)))
    return {
        "total_findings": len(findings),
        "critical_count": counts.get("Critical", 0),
        "high_count": counts.get("High", 0),
        "medium_count": counts.get("Medium", 0),
        "low_count": counts.get("Low", 0),
        "risk_score": risk_score,
        "security_score": security_score,
    }


def run_scan(file_name: str, content: str) -> Dict[str, Any]:
    raw_findings = run_pipeline_sync(file_name, content)
    findings = [normalize_vulnerability(v) for v in raw_findings]
    summary = _summarize(findings)
    summary_payload = {
        "total": summary["total_findings"],
        "critical": summary["critical_count"],
        "high": summary["high_count"],
        "medium": summary["medium_count"],
        "low": summary["low_count"],
        "risk_score": summary["risk_score"],
        "security_score": summary["security_score"],
    }

    return {
        "file_name": Path(file_name).as_posix(),
        "vulnerabilities": findings,
        **summary,
        "scan_engine": "DristiScan Orchestrator v2",
        "rules_applied": len(_rule_engine.rules),
        "summary": summary_payload,
    }


def get_rule_count() -> int:
    return len(_rule_engine.rules)
