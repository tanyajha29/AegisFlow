from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

SCHEMA_EXAMPLE = """
[
  {
    "title": "",
    "severity": "",
    "description": "",
    "remediation": "",
    "file": "",
    "line": 0,
    "detected_by": ["Secrets Agent"]
  }
]
""".strip()


class SecretsAgent(BaseAgent):
    """
    AI-powered helper that asks Ollama to flag exposed secrets/credentials.
    """

    def build_prompt(self, code: str, file_name: Optional[str]) -> str:
        file_hint = file_name or "the file being scanned"
        return (
            "You are a secrets-detection specialist.\n"
            "Analyze the provided code ONLY for exposed secrets and credentials:\n"
            "- API keys\n"
            "- access tokens\n"
            "- private keys\n"
            "- hardcoded passwords\n"
            "- exposed credentials\n"
            "Return ONLY valid JSON. No markdown, no code fences, no explanations outside JSON.\n"
            "Use exactly this schema:\n"
            f"{SCHEMA_EXAMPLE}\n"
            "Rules:\n"
            "- If no secrets are present, return an empty JSON array []\n"
            "- Use integers for the line field; use 0 when the line is unknown\n"
            f"- Set the file field to '{file_hint}' when unsure\n"
            "Now analyze the following code and respond with JSON only:\n"
            f"File: {file_hint}\n"
            f"{code}\n"
        )

    def _normalize(self, data: Any, file_name: Optional[str]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        if not isinstance(data, list):
            return []

        for item in data:
            if not isinstance(item, dict):
                continue

            title = (item.get("title") or "Secrets Exposure").strip()
            severity_raw = item.get("severity") or "High"
            severity = str(severity_raw).strip().title()
            description = str(item.get("description") or "").strip()
            remediation = str(
                item.get("remediation") or "Rotate the secret, remove it from code, and move to a secure store."
            ).strip()
            file_value = str(item.get("file") or file_name or "unknown").strip()

            line_raw = item.get("line", 0)
            try:
                line_num = int(line_raw) if line_raw is not None else 0
            except (TypeError, ValueError):
                line_num = 0

            detected_by = item.get("detected_by") or []
            if isinstance(detected_by, str):
                detected_by = [detected_by]
            detected_by = list(detected_by)
            if "Secrets Agent" not in detected_by:
                detected_by.append("Secrets Agent")

            normalized.append(
                {
                    "title": title,
                    "severity": severity,
                    "description": description,
                    "remediation": remediation,
                    "file": file_value,
                    "line": line_num,
                    "detected_by": detected_by or ["Secrets Agent"],
                }
            )

        return normalized

    def analyze(self, code: str, file_name: Optional[str] = None) -> List[Dict[str, Any]]:
        prompt = self.build_prompt(code, file_name)
        raw = self.send_prompt(prompt)
        parsed = self.safe_json_loads(raw)
        findings = self._normalize(parsed, file_name) if parsed is not None else []
        if not findings and raw and parsed is None:
            logger.warning("Secrets Agent received non-JSON response; returning empty findings.")
        return findings


def run_secrets_agent(code: str, file_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function that runs the secrets agent and returns normalized findings.
    """
    agent = SecretsAgent()
    return agent.analyze(code=code, file_name=file_name)
