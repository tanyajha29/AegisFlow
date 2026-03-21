from __future__ import annotations

import logging
from typing import Dict, List

from app.agents.orchestrator import run_ai_orchestration

logger = logging.getLogger("dristi-scan")


def _convert_agent_findings(file_name: str, findings) -> List[Dict]:
    converted = []
    for f in findings:
        converted.append(
            {
                "name": f.title,
                "severity": f.severity,
                "file_name": f.file or file_name,
                "line_number": f.line,
                "description": f.description,
                "remediation": f.remediation,
                "cwe_reference": None,
                "code_snippet": None,
                "category": "AI Agent",
                "detected_by": f.detected_by,
                "confidence": f.confidence,
                "agent_source": "ai_agent",
            }
        )
    return converted


async def analyze_with_ai(file_name: str, content: str) -> Dict:
    """
    Use AI agent orchestrator to get structured findings.
    Returns dict with keys: findings (list), agents_used (list), logs (list).
    """
    try:
        orchestration = run_ai_orchestration(content=content, file_path=file_name)
    except Exception as exc:
        logger.warning("AI orchestration failed: %s", exc)
        return {"findings": [], "agents_used": [], "logs": [f"[AI] Error: {exc}"]}

    converted = _convert_agent_findings(file_name, orchestration.findings)
    return {
        "findings": converted,
        "agents_used": orchestration.agents_used,
        "logs": orchestration.logs,
        "raw_agent_results": [r.model_dump() for r in orchestration.agent_results],
    }
