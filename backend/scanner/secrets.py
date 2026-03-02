import re

SECRET_RULES = [
    {
        "name": "AWS Access Key",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "Critical",
        "cwe": "CWE-798",
        "explanation": "Hardcoded AWS Access Key ID detected.",
        "remediation_steps": "Remove from source code and use environment variables or AWS IAM roles."
    },
    {
        "name": "Generic API Key or Secret",
        "pattern": r"(?i)(api_key|apikey|secret|password|token)\s*=\s*['\"][A-Za-z0-9\-_]{16,}['\"]",
        "severity": "High",
        "cwe": "CWE-798",
        "explanation": "Hardcoded generic API Key or secret detected.",
        "remediation_steps": "Move secret to environment variables (.env files) or a secret manager."
    },
    {
        "name": "JWT Token",
        "pattern": r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "severity": "Medium",
        "cwe": "CWE-798",
        "explanation": "Hardcoded JWT Token detected. Tokens should not be checked into VC.",
        "remediation_steps": "Remove the token from source code."
    },
    {
        "name": "RSA Private Key",
        "pattern": r"-----BEGIN RSA PRIVATE KEY-----",
        "severity": "Critical",
        "cwe": "CWE-798",
        "explanation": "Hardcoded RSA Private Key detected.",
        "remediation_steps": "Remove private keys from source code."
    }
]

def scan_file_secrets(filepath: str, filename: str) -> list:
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            for rule in SECRET_RULES:
                if re.search(rule["pattern"], line):
                    results.append({
                        "vulnerability_name": rule["name"],
                        "severity": rule["severity"],
                        "file_name": filename,
                        "line_number": line_num,
                        "code_snippet": line.strip()[:200],
                        "explanation": rule["explanation"],
                        "remediation_steps": rule["remediation_steps"],
                        "cwe_mapping": rule["cwe"]
                    })
    except Exception as e:
        print(f"Error scanning file for Secrets {filepath}: {e}")
    
    return results
