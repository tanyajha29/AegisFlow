import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from app.agents.injection_agent import run_injection_agent
from app.agents.secrets_agent import run_secrets_agent

from .rule_engine import RuleEngineScanner
from ..scanners.sast_scanner import scan_code as sast_scan
from ..scanners.secret_scanner import scan_for_secrets
from ..scanners.dependency_scanner import scan_dependencies


_rule_engine = RuleEngineScanner()


def _write_temp_file(file_name: str, content: str) -> Path:
    tmp_dir = tempfile.mkdtemp(prefix="dristiscan_")
    path = Path(tmp_dir) / Path(file_name).name
    path.write_text(content, encoding="utf-8", errors="ignore")
    return path


def run_semgrep(file_name: str, content: str) -> List[Dict[str, Any]]:
    """
    Optional Semgrep integration. If semgrep is unavailable, returns empty list.
    """
    if not shutil.which("semgrep"):
        return []
    temp_path = _write_temp_file(file_name, content)
    try:
        import subprocess
        import json

        cmd = ["semgrep", "--config", "auto", "--json", str(temp_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode not in (0, 1):  # 1 = findings
            return []
        data = json.loads(result.stdout or "{}")
        findings = []
        for item in data.get("results", []):
            findings.append(
                {
                    "name": item.get("check_id", "Semgrep Finding"),
                    "severity": item.get("extra", {}).get("severity", "Medium").title(),
                    "file_name": Path(file_name).name,
                    "line_number": item.get("start", {}).get("line"),
                    "description": item.get("extra", {}).get("message", ""),
                    "remediation": item.get("extra", {}).get("metadata", {}).get("fix", "Review and fix."),
                    "cwe_reference": None,
                    "code_snippet": item.get("extra", {}).get("lines"),
                    "category": "Semgrep",
                }
            )
        return findings
    finally:
        shutil.rmtree(temp_path.parent, ignore_errors=True)


def run_bandit(file_name: str, content: str) -> List[Dict[str, Any]]:
    if not shutil.which("bandit"):
        return []
    temp_path = _write_temp_file(file_name, content)
    try:
        import subprocess
        import json

        cmd = ["bandit", "-q", "-r", str(temp_path.parent), "-f", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        data = json.loads(result.stdout or "{}")
        findings = []
        for item in data.get("results", []):
            findings.append(
                {
                    "name": item.get("test_name", "Bandit Finding"),
                    "severity": item.get("issue_severity", "Medium").title(),
                    "file_name": Path(file_name).name,
                    "line_number": item.get("line_number"),
                    "description": item.get("issue_text", ""),
                    "remediation": item.get("more_info", "Review and fix."),
                    "cwe_reference": item.get("cwe", {}).get("id"),
                    "code_snippet": item.get("code", ""),
                    "category": "Bandit",
                }
            )
        return findings
    finally:
        shutil.rmtree(temp_path.parent, ignore_errors=True)


def _convert_injection_findings(ai_findings: List[Dict[str, Any]], file_name: str) -> List[Dict[str, Any]]:
    """
    Map Injection Agent output into the shared vulnerability structure.
    """
    converted: List[Dict[str, Any]] = []
    for item in ai_findings:
        if not isinstance(item, dict):
            continue

        converted.append(
            {
                "name": item.get("title") or "Injection Finding",
                "severity": str(item.get("severity") or "Medium").title(),
                "description": item.get("description") or "",
                "remediation": item.get("remediation") or "Review and fix the issue.",
                "file_name": item.get("file") or Path(file_name).name,
                "line_number": item.get("line") if item.get("line") not in ("", None) else None,
                "category": "Injection Agent",
                "detected_by": item.get("detected_by") or ["Injection Agent"],
            }
        )
    return converted


def _convert_secret_findings(ai_findings: List[Dict[str, Any]], file_name: str) -> List[Dict[str, Any]]:
    """
    Map Secrets Agent output into the shared vulnerability structure.
    """
    converted: List[Dict[str, Any]] = []
    for item in ai_findings:
        if not isinstance(item, dict):
            continue

        converted.append(
            {
                "name": item.get("title") or "Secrets Exposure",
                "severity": str(item.get("severity") or "High").title(),
                "description": item.get("description") or "",
                "remediation": item.get("remediation")
                or "Rotate the secret, remove it from code, and store it securely.",
                "file_name": item.get("file") or Path(file_name).name,
                "line_number": item.get("line") if item.get("line") not in ("", None) else None,
                "category": "Secrets Agent",
                "detected_by": item.get("detected_by") or ["Secrets Agent"],
            }
        )
    return converted


async def run_pipeline(file_name: str, content: str) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    """
    Modular pipeline:
    - Rule/heuristic scanners
    - Optional third-party tools
    - Injection Agent (Ollama)
    - Secrets Agent (Ollama)
    Returns (findings, ai_meta).
    """
    findings: List[Dict[str, Any]] = []
    findings.extend(_rule_engine.scan(content, file_name))
    findings.extend(sast_scan(content, file_name))
    findings.extend(scan_for_secrets(content, file_name))
    findings.extend(scan_dependencies(file_name, content))
    findings.extend(run_semgrep(file_name, content))
    findings.extend(run_bandit(file_name, content))

    ai_meta: Dict[str, Any] = {
        "findings": [],
        "agents_used": [],
        "logs": [],
        "raw_agent_results": [],
    }

    # Injection Agent runs after traditional scanners
    try:
        ai_raw = run_injection_agent(content, file_name=file_name)
        ai_meta["raw_agent_results"].append({"agent": "Injection Agent", "raw": ai_raw})
        converted = _convert_injection_findings(ai_raw, file_name)
        if converted:
            ai_meta["findings"].extend(converted)
            ai_meta["agents_used"].append("Injection Agent")
        ai_meta["logs"].append(f"Injection Agent completed ({len(ai_raw)} findings reported).")
        findings.extend(converted)
    except Exception as exc:  # pragma: no cover - defensive guard
        ai_meta["logs"].append(f"Injection Agent error: {exc}")

    # Secrets Agent runs after Injection Agent
    try:
        secrets_raw = run_secrets_agent(content, file_name=file_name)
        ai_meta["raw_agent_results"].append({"agent": "Secrets Agent", "raw": secrets_raw})
        secrets_converted = _convert_secret_findings(secrets_raw, file_name)
        if secrets_converted:
            ai_meta["findings"].extend(secrets_converted)
            ai_meta["agents_used"].append("Secrets Agent")
        ai_meta["logs"].append(f"Secrets Agent completed ({len(secrets_raw)} findings reported).")
        findings.extend(secrets_converted)
    except Exception as exc:  # pragma: no cover - defensive guard
        ai_meta["logs"].append(f"Secrets Agent error: {exc}")

    return findings, ai_meta


def run_pipeline_sync(file_name: str, content: str) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    """
    Wrapper for sync contexts.
    """
    return asyncio.run(run_pipeline(file_name, content))
