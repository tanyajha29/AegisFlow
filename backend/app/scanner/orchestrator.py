import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

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


async def run_pipeline(file_name: str, content: str) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    """
    Modular pipeline that can be extended easily.
    Returns (findings, ai_meta). AI metadata is empty because agents are disabled.
    """
    findings: List[Dict[str, Any]] = []
    findings.extend(_rule_engine.scan(content, file_name))
    findings.extend(sast_scan(content, file_name))
    findings.extend(scan_for_secrets(content, file_name))
    findings.extend(scan_dependencies(file_name, content))
    findings.extend(run_semgrep(file_name, content))
    findings.extend(run_bandit(file_name, content))

    ai_meta = {
        "findings": [],
        "agents_used": [],
        "logs": ["AI agents are disabled; rule-based scanners only."],
        "raw_agent_results": [],
    }
    return findings, ai_meta


def run_pipeline_sync(file_name: str, content: str) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    """
    Wrapper for sync contexts.
    """
    return asyncio.run(run_pipeline(file_name, content))
