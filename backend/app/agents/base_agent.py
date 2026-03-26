from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional

import requests
from requests import Response

from app.agents.schemas import AgentResult

logger = logging.getLogger(__name__)


DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "deepseek-coder"
DEFAULT_TIMEOUT_SECONDS = 120


def _normalize_endpoint(url: str) -> str:
    """Ensure we target the Ollama /api/generate endpoint even if a base URL is provided."""
    cleaned = (url or "").rstrip("/")
    if cleaned.endswith("/api/generate"):
        return cleaned
    if cleaned.endswith("/api"):
        return f"{cleaned}/generate"
    return f"{cleaned}/api/generate" if cleaned else DEFAULT_OLLAMA_URL


class BaseAgent:
    """
    Lightweight, reusable helper for calling an Ollama model with a prompt.
    Uses environment variables:
    - OLLAMA_URL (default http://localhost:11434/api/generate)
    - OLLAMA_MODEL (default deepseek-coder)
    - OLLAMA_TIMEOUT_SECONDS (default 120)
    - RAG_DEBUG (default false) — enables verbose prompt/response logging
    """

    def __init__(
        self,
        name: str | None = None,
        system_instructions: Optional[str] = None,
        model: Optional[str] = None,
        url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> None:
        self.name = name or "Base Agent"
        self.system_instructions = (system_instructions or "").strip()
        self.model = (model or os.getenv("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip()
        raw_url = url or os.getenv("OLLAMA_URL") or DEFAULT_OLLAMA_URL
        self.url = _normalize_endpoint(raw_url)
        try:
            self.timeout = float(
                timeout_seconds or os.getenv("OLLAMA_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
            )
        except (TypeError, ValueError):
            self.timeout = float(DEFAULT_TIMEOUT_SECONDS)

        self._debug = os.getenv("RAG_DEBUG", "false").lower() in ("1", "true", "yes")

    # ---- HTTP helpers -------------------------------------------------
    def _post(self, prompt: str) -> Response:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        return requests.post(self.url, json=payload, timeout=self.timeout)

    def send_prompt(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and return the raw text response.
        Returns an empty string on any failure to keep callers safe.
        """
        if self._debug:
            logger.debug(
                "[%s] Sending prompt to %s (model=%s, timeout=%ss):\n%s",
                self.name, self.url, self.model, self.timeout, prompt[:600],
            )
        try:
            response = self._post(prompt)
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError:
                logger.warning("[%s] Ollama response was not JSON-decodable; returning empty.", self.name)
                return ""

            text = data.get("response") or data.get("output") or ""
            if isinstance(text, str):
                result = text.strip()
                if self._debug:
                    logger.debug(
                        "[%s] Raw Ollama response (%d chars):\n%s",
                        self.name, len(result), result[:800],
                    )
                return result
            logger.warning("[%s] Unexpected Ollama payload shape; expected 'response' text.", self.name)
            return ""
        except requests.Timeout:
            logger.error(
                "[%s] Ollama request timed out after %ss (url=%s). "
                "Increase OLLAMA_TIMEOUT_SECONDS if the model is slow.",
                self.name, self.timeout, self.url,
            )
            return ""
        except requests.ConnectionError as exc:
            logger.error(
                "[%s] Ollama connection refused (is Ollama running at %s?): %s",
                self.name, self.url, exc,
            )
            return ""
        except requests.RequestException as exc:
            logger.error("[%s] Ollama request failed: %s", self.name, exc)
            return ""
        except Exception as exc:  # pragma: no cover
            logger.error("[%s] Unhandled error when calling Ollama: %s", self.name, exc)
            return ""

    # ---- JSON parsing helpers -----------------------------------------
    @staticmethod
    def safe_json_loads(text: str) -> Any:
        """
        Attempt to parse JSON while tolerating:
        - markdown code fences (```json ... ``` or ``` ... ```)
        - leading/trailing prose around a JSON object or array
        Returns None on failure and logs the reason.
        """
        if not text:
            return None

        # 1. Direct parse — fastest path
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Strip markdown code fences
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
        if fence_match:
            candidate = fence_match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # 3. Extract first JSON object or array from surrounding prose
        for pattern in (r"\{[\s\S]*\}", r"\[[\s\S]*\]"):
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    continue

        logger.warning(
            "safe_json_loads: could not extract valid JSON from response (len=%d, preview=%r)",
            len(text), text[:120],
        )
        return None

    @staticmethod
    def ensure_list_of_dicts(payload: Any) -> list[dict[str, Any]]:
        """Normalize arbitrary JSON payloads into a list of dicts."""
        if not payload:
            return []
        if isinstance(payload, dict):
            return [payload]
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    # ---- Compatibility runner for other agents ------------------------
    def build_prompt(self, code_snippet: str, task: str, instructions: Optional[str] = None) -> str:
        parts = []
        if self.system_instructions:
            parts.append(self.system_instructions)
        if instructions:
            parts.append(instructions.strip())
        if task:
            parts.append(task.strip())
        parts.append("Return ONLY valid JSON. No markdown or code fences.")
        parts.append(f"Input:\n{code_snippet}")
        return "\n\n".join(parts)

    def run(self, code_snippet: str, task: str, instructions: Optional[str] = None) -> AgentResult:
        """Backwards-compatible runner that returns an AgentResult."""
        prompt = self.build_prompt(code_snippet, task, instructions)
        raw = self.send_prompt(prompt)
        parsed = self.safe_json_loads(raw)
        if parsed is None:
            return AgentResult(
                agent=self.name, findings=[], logs=[f"[{self.name}] Invalid or empty response."]
            )
        try:
            result = AgentResult.model_validate(parsed)
        except Exception as exc:  # pragma: no cover
            logger.warning("Agent %s returned invalid payload: %s", self.name, exc)
            return AgentResult(
                agent=self.name, findings=[], logs=[f"[{self.name}] Invalid response ignored: {exc}"]
            )
        if not result.agent:
            result.agent = self.name
        return result


# Backwards compatibility helper used by older tests or utilities.
class TestEchoAgent(BaseAgent):
    def analyze(self, text: str) -> list[dict[str, Any]]:
        prompt = f"Echo back an empty JSON array. Input length: {len(text)}"
        raw = self.send_prompt(prompt)
        parsed = self.safe_json_loads(raw)
        return self.ensure_list_of_dicts(parsed)
