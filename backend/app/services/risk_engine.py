from typing import Iterable, Tuple

SEVERITY_WEIGHTS = {
    "Critical": 40,
    "High": 25,
    "Medium": 15,
    "Low": 5,
}


def calculate_risk_score(severities: Iterable[str]) -> float:
    total_points = sum(SEVERITY_WEIGHTS.get(sev, 0) for sev in severities)
    return float(min(100.0, total_points))


def risk_level(score: float) -> str:
    if score >= 80:
        return "Critical Risk"
    if score >= 50:
        return "High Risk"
    if score >= 20:
        return "Medium Risk"
    return "Low Risk"


def summarize_vulnerabilities(vulnerabilities) -> Tuple[float, int]:
    severities = [v.severity if hasattr(v, "severity") else v["severity"] for v in vulnerabilities]
    return calculate_risk_score(severities), len(severities)
