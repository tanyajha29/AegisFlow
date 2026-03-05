import re
from pathlib import Path
from typing import Any, Dict, List

SECRET_PATTERNS = [
    {
        "name": "AWS Access Key",
        "severity": "High",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "description": "AWS access key detected in code.",
        "remediation": "Remove keys from source and rotate credentials.",
        "cwe_reference": "CWE-798",
    },
    {
        "name": "AWS Secret Key",
        "severity": "High",
        "pattern": r"(?i)aws_secret_access_key\\s*[=:]\\s*[0-9a-zA-Z/+]{40}",
        "description": "AWS secret access key exposed.",
        "remediation": "Use IAM roles or secret managers; rotate key.",
        "cwe_reference": "CWE-798",
    },
    {
        "name": "Generic API Key",
        "severity": "Medium",
        "pattern": r"(?i)(api_key|apikey|token|secret)\\s*[:=]\\s*['\\\"][0-9a-zA-Z-_]{16,}['\\\"]",
        "description": "Likely API key or token hardcoded.",
        "remediation": "Move secrets to environment variables or secret storage.",
        "cwe_reference": "CWE-798",
    },
    {
        "name": "Private Key",
        "severity": "Critical",
        "pattern": r"-----BEGIN( RSA)? PRIVATE KEY-----",
        "description": "Private key block found in source.",
        "remediation": "Remove private keys, rotate credentials, and use secure storage.",
        "cwe_reference": "CWE-321",
    },
    {
        "name": "JWT Token",
        "severity": "Low",
        "pattern": r"eyJ[a-zA-Z0-9_-]{10,}\\.[a-zA-Z0-9._-]+\\.[a-zA-Z0-9._-]+",
        "description": "JWT token present in source.",
        "remediation": "Avoid embedding tokens in code; use secure storage.",
        "cwe_reference": "CWE-522",
    },
]


def scan_for_secrets(content: str, file_name: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    lines = content.splitlines()
    for rule in SECRET_PATTERNS:
        regex = re.compile(rule["pattern"])
        for idx, line in enumerate(lines, start=1):
            if regex.search(line):
                findings.append(
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
    return findings

