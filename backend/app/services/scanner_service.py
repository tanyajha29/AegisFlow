from pathlib import Path
from typing import List, Dict, Any

from ..scanners.sast_scanner import scan_code as sast_scan
from ..scanners.secret_scanner import scan_for_secrets
from ..scanners.dependency_scanner import scan_dependencies


def run_scanners(file_name: str, content: str) -> List[Dict[str, Any]]:
    """
    Run SAST, secret, and dependency scanners on provided content.
    """
    vulnerabilities: List[Dict[str, Any]] = []
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
    }
    normalized = {**defaults, **vuln}
    normalized["file_name"] = Path(vuln.get("file_name", "unknown.txt")).name
    return normalized

