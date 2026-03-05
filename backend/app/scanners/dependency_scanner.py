import json
from pathlib import Path
from typing import Any, Dict, List

KNOWN_VULNERABILITIES = {
    "django": [
        ("<4.2.11", "High", "Django security patches missing (CVE-2024-24680)."),
    ],
    "requests": [
        ("<2.32.0", "Medium", "Requests before 2.32.0 vulnerable to header injection."),
    ],
    "lodash": [
        ("<4.17.21", "High", "Prototype pollution vulnerability in lodash."),
    ],
    "express": [
        ("<4.18.2", "High", "Known DoS and XSS issues in older Express versions."),
    ],
}


def _version_is_vulnerable(version: str, constraint: str) -> bool:
    # very small comparator supporting "<" prefix
    if not version or not constraint.startswith("<"):
        return False
    try:
        from packaging import version as pkg_version
    except ImportError:
        # best-effort fallback: string compare
        return version < constraint[1:]
    return pkg_version.parse(version) < pkg_version.parse(constraint[1:])


def _build_vuln(package: str, severity: str, description: str, file_name: str) -> Dict[str, Any]:
    return {
        "name": f"Vulnerable dependency: {package}",
        "severity": severity,
        "file_name": file_name,
        "line_number": None,
        "description": description,
        "remediation": f"Upgrade {package} to a safe version per advisory.",
        "cwe_reference": "CWE-937",
        "code_snippet": None,
    }


def _parse_requirements(content: str) -> Dict[str, str | None]:
    deps: Dict[str, str | None] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            pkg, ver = line.split("==", 1)
            deps[pkg.strip().lower()] = ver.strip()
        else:
            deps[line.lower()] = None
    return deps


def _parse_package_json(content: str) -> Dict[str, str | None]:
    deps: Dict[str, str | None] = {}
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return deps
    for section in ("dependencies", "devDependencies"):
        for name, ver in data.get(section, {}).items():
            deps[name.lower()] = ver.lstrip("^~")
    return deps


def scan_dependencies(file_name: str, content: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    ext = Path(file_name).suffix.lower()
    deps: Dict[str, str | None] = {}
    if ext in {".txt", ".pip", ".req", ".cfg", ".ini"} or file_name.lower() == "requirements.txt":
        deps = _parse_requirements(content)
    elif ext == ".json" and "package.json" in file_name:
        deps = _parse_package_json(content)

    for pkg, version in deps.items():
        advisories = KNOWN_VULNERABILITIES.get(pkg)
        if not advisories:
            continue
        for constraint, severity, description in advisories:
            if _version_is_vulnerable(version or "", constraint):
                findings.append(_build_vuln(pkg, severity, description, Path(file_name).name))
                break

    return findings

