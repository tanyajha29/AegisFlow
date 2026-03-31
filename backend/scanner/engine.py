import os
from .sast import scan_file_sast
from .secrets import scan_file_secrets
from .dependencies import scan_dependencies

def calculate_risk_score(vulnerabilities: list) -> float:
    # A simple scoring algorithm based on severity weights
    weights = {
        "Critical": 10.0,
        "High": 7.0,
        "Medium": 4.0,
        "Low": 1.0
    }
    
    total_score = 0
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'Low')
        total_score += weights.get(severity, 0)
        
    # Cap stringently or average it depending on the design preference.
    # Here, let's max out at 100 for gauge visualization.
    score = min(total_score, 100.0)
    return float(score)

def run_scan(scan_dir: str) -> tuple[list, float]:
    """Iterates over files in scan_dir and runs applicable scanners."""
    all_vulnerabilities = []
    
    for root, dirs, files in os.walk(scan_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # 1. Dependency Scanner
            if filename in ["requirements.txt", "package.json"]:
                deps_vulns = scan_dependencies(filepath, filename)
                all_vulnerabilities.extend(deps_vulns)
                
            # 2. Secret & SAST Scanner (Text files typically)
            # Ignoring binary files implicitly by handling try/except blocks inside scanner logic
            secrets_vulns = scan_file_secrets(filepath, filename)
            all_vulnerabilities.extend(secrets_vulns)
            
            # We enforce SAST only on typical source extensions to prevent unnecessary scanning
            sast_extensions = ('.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cs', '.php', '.rb', '.go')
            if filename.endswith(sast_extensions) or "." not in filename: # "no extension" for snippets
                sast_vulns = scan_file_sast(filepath, filename)
                all_vulnerabilities.extend(sast_vulns)
                
    risk_score = calculate_risk_score(all_vulnerabilities)
    return all_vulnerabilities, risk_score
