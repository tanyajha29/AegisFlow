from __future__ import annotations

import logging
from typing import Dict, List

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
    AI agents are currently disabled. Returns empty metadata for compatibility.
    """
    return {
        "findings": [],
        "agents_used": [],
        "logs": ["AI agents are disabled; rule-based scanners only."],
        "raw_agent_results": [],
    }
