from pathlib import Path
from typing import List, Dict, Any

from ..scanners.sast_scanner import scan_code as sast_scan
from ..scanners.secret_scanner import scan_for_secrets
from ..scanners.dependency_scanner import scan_dependencies
from ..scanner.rule_engine import RuleEngineScanner

_rule_engine = RuleEngineScanner()


def run_scanners(file_name: str, content: str) -> List[Dict[str, Any]]:
    """
    Run custom rule engine plus SAST, secret, and dependency scanners.
    """
    vulnerabilities: List[Dict[str, Any]] = []
    vulnerabilities.extend(_rule_engine.scan(content, file_name))
    vulnerabilities.extend(sast_scan(content, file_name))
    vulnerabilities.extend(scan_for_secrets(content, file_name))
    vulnerabilities.extend(scan_dependencies(file_name, content))
    return vulnerabilities


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
    normalized["file_name"] = Path(vuln.get("file_name", "unknown.txt")).name
    return normalized
