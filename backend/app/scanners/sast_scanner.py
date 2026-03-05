import re
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_RULES = [
    {
        "name": "SQL Injection",
        "severity": "Critical",
        "pattern": r"(execute\(|raw\s*\().*(SELECT|INSERT|UPDATE|DELETE).*(\+|format\(|%s)",
        "description": "User input concatenated into SQL statements can lead to injection.",
        "remediation": "Use parameterized queries or ORM query builders.",
        "cwe_reference": "CWE-89",
    },
    {
        "name": "Command Injection",
        "severity": "High",
        "pattern": r"(os\.system|subprocess\.Popen|subprocess\.call).*\+.*",
        "description": "Concatenating user input into shell commands is unsafe.",
        "remediation": "Avoid shell=True; validate inputs; use parameter arrays.",
        "cwe_reference": "CWE-78",
    },
    {
        "name": "Insecure Eval",
        "severity": "High",
        "pattern": r"(eval\s*\(|exec\s*\()",
        "description": "Executing dynamic code allows arbitrary code execution.",
        "remediation": "Remove dynamic execution or strictly sandbox inputs.",
        "cwe_reference": "CWE-95",
    },
    {
        "name": "Insecure File Access",
        "severity": "Medium",
        "pattern": r"open\s*\(.*(\+|format\(|%s)",
        "description": "Unvalidated path construction may allow path traversal.",
        "remediation": "Validate and normalize file paths; avoid user-controlled file names.",
        "cwe_reference": "CWE-22",
    },
    {
        "name": "XSS Output",
        "severity": "Medium",
        "pattern": r"(innerHTML\s*=|document\.write\()",
        "description": "Writing unsanitized data to DOM can lead to XSS.",
        "remediation": "Use safe templating and output encoding.",
        "cwe_reference": "CWE-79",
    },
]


def scan_code(content: str, file_name: str) -> List[Dict[str, Any]]:
    vulnerabilities: List[Dict[str, Any]] = []
    lines = content.splitlines()

    for rule in DEFAULT_RULES:
        regex = re.compile(rule["pattern"], re.IGNORECASE)
        for idx, line in enumerate(lines, start=1):
            if regex.search(line):
                vulnerabilities.append(
                    {
                        "name": rule["name"],
                        "severity": rule["severity"],
                        "file_name": Path(file_name).name,
                        "line_number": idx,
                        "description": rule["description"],
                        "remediation": rule["remediation"],
                        "cwe_reference": rule["cwe_reference"],
                        "code_snippet": line.strip(),
                    }
                )
    return vulnerabilities
