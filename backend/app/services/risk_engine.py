from typing import Iterable, Tuple

SEVERITY_WEIGHTS = {
    "Critical": 10,
    "High": 7,
    "Medium": 4,
    "Low": 2,
}


def calculate_risk_score(severities: Iterable[str]) -> float:
    total_points = sum(SEVERITY_WEIGHTS.get(sev, 0) for sev in severities)
    score = max(0.0, 100.0 - float(total_points))
    return round(score, 2)


def risk_level(score: float) -> str:
    if score < 40:
        return "High Risk"
    if score < 70:
        return "Medium Risk"
    return "Low Risk"


def summarize_vulnerabilities(vulnerabilities) -> Tuple[float, int]:
    severities = [v.severity if hasattr(v, "severity") else v["severity"] for v in vulnerabilities]
    return calculate_risk_score(severities), len(severities)

