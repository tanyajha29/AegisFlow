import re

SAST_RULES = [
    {
        "name": "SQL Injection Risk",
        "pattern": r"SELECT\s+.*FROM\s+.*WHERE\s+.*\+.*|f\"SELECT.*{.*}\"",
        "severity": "Critical",
        "cwe": "CWE-89",
        "explanation": "Potential SQL injection detected. String concatenation or interpolation used in SQL query.",
        "remediation_steps": "Use parameterized queries or ORM models instead of raw string formatting."
    },
    {
        "name": "Cross-Site Scripting (XSS)",
        "pattern": r"innerHtml\s*=\s*.*|document\.write\(.*\)",
        "severity": "High",
        "cwe": "CWE-79",
        "explanation": "Direct DOM manipulation with potentially unsanitized data.",
        "remediation_steps": "Sanitize user input before rendering or use safer frameworks that auto-escape strings."
    },
    {
        "name": "Command Injection",
        "pattern": r"os\.system\(.*\)|subprocess\.Popen\(.*\+.*\)|child_process\.exec\(.*\)",
        "severity": "Critical",
        "cwe": "CWE-78",
        "explanation": "Execution of OS commands using concatenated strings is dangerous.",
        "remediation_steps": "Pass commands and arguments as array lists to subprocess, and never trust user input in commands."
    },
    {
        "name": "Unsafe eval() usage",
        "pattern": r"eval\(.*\)",
        "severity": "Critical",
        "cwe": "CWE-95",
        "explanation": "The eval() function is dangerous because it executes arbitrary code.",
        "remediation_steps": "Avoid using eval(). If parsing JSON, use json.loads(). For safe evaluation, use ast.literal_eval()."
    },
    {
        "name": "Insecure Cryptography Usage",
        "pattern": r"MD5\(|hashlib\.md5|SHA1\(|hashlib\.sha1",
        "severity": "Medium",
        "cwe": "CWE-327",
        "explanation": "MD5 and SHA1 are considered weak cryptographic hashes.",
        "remediation_steps": "Upgrade to a stronger hash function like SHA-256 or bcrypt (for passwords)."
    }
]

def scan_file_sast(filepath: str, filename: str) -> list:
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            for rule in SAST_RULES:
                if re.search(rule["pattern"], line, re.IGNORECASE):
                    results.append({
                        "vulnerability_name": rule["name"],
                        "severity": rule["severity"],
                        "file_name": filename,
                        "line_number": line_num,
                        "code_snippet": line.strip()[:200], # Trucate long lines
                        "explanation": rule["explanation"],
                        "remediation_steps": rule["remediation_steps"],
                        "cwe_mapping": rule["cwe"]
                    })
    except Exception as e:
        print(f"Error scanning file for SAST {filepath}: {e}")
    
    return results
