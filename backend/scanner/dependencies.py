import re
import json

# A mock database of vulnerable package versions for demonstration purposes.
VULNERABLE_PACKAGES = {
    "django": {
        "vulnerable_versions": ["<3.2.19"],
        "severity": "High",
        "cwe": "CWE-400",
        "explanation": "Denial of service vulnerability in Django < 3.2.19 via excessive file uploads.",
        "remediation_steps": "Upgrade django to 3.2.19 or higher."
    }, 
    "requests": { 
        "vulnerable_versions": ["<2.31.0"],
        "severity": "Medium",
        "cwe": "CWE-400",
        "explanation": "Potential unintended leak of Proxy-Authorization header in requests < 2.31.0.",
        "remediation_steps": "Upgrade requests to 2.31.0 or higher."
    },
    "lodash": {
        "vulnerable_versions": ["<4.17.21"],
        "severity": "High",
        "cwe": "CWE-400",
        "explanation": "Prototype pollution in lodash < 4.17.21.",
        "remediation_steps": "Upgrade lodash to 4.17.21 or higher."
    }
}

def check_version(pkg_name: str, version: str) -> dict:
    pkg = VULNERABLE_PACKAGES.get(pkg_name.lower())
    if not pkg:
        return None
        
    # Simplified version comparison for demo purposes
    vuln_vers = pkg["vulnerable_versions"][0]
    if vuln_vers.startswith("<"):
        target_version = vuln_vers[1:]
        # A simple string comparison for versions (in production use a proper semver parser)
        if version < target_version or version.startswith("="): 
            return {
                "vulnerability_name": f"Vulnerable package: {pkg_name} {version}",
                "severity": pkg["severity"],
                "explanation": pkg["explanation"],
                "remediation_steps": pkg["remediation_steps"],
                "cwe_mapping": pkg["cwe"]
            }
    return None

def scan_dependencies(filepath: str, filename: str) -> list:
    results = []
    try:
        if filename.endswith("requirements.txt"):
            with open(filepath, 'r') as f:
                lines = f.readlines()
            for line_num, line in enumerate(lines, 1):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#"):
                    continue
                parts = re.split(r'==|>=|<=|~=|<|>', clean_line)
                if len(parts) >= 2:
                    pkg_name = parts[0].strip()
                    version = parts[1].strip()
                    vuln = check_version(pkg_name, version)
                    if vuln:
                        vuln.update({
                            "file_name": filename,
                            "line_number": line_num,
                            "code_snippet": clean_line
                        })
                        results.append(vuln)
                        
        elif filename.endswith("package.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            # Since package.json doesn't easily give line numbers, we default to 1
            for pkg_name, version in all_deps.items():
                clean_version = version.replace("^", "").replace("~", "")
                vuln = check_version(pkg_name, clean_version)
                if vuln:
                    vuln.update({
                        "file_name": filename,
                        "line_number": 1,
                        "code_snippet": f'"{pkg_name}": "{version}"'
                    })
                    results.append(vuln)

    except Exception as e:
        print(f"Error scanning dependencies {filepath}: {e}")
        
    return results
