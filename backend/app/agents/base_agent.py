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
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder"
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
        payload = {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}
        return requests.post(self.url, json=payload, timeout=self.timeout)

    def send_prompt(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and return the raw text response.
        Returns an empty string on any failure to keep callers safe.
        """
        if self._debug:
            logger.debug(
                "[%s] Sending prompt to %s (model=%s, timeout=%ss):\n%s",
                self.name, self.url, self.model, self.timeout, prompt[:800],
            )
        else:
            logger.info("[%s] Calling Ollama model=%s timeout=%ss", self.name, self.model, self.timeout)
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
                        self.name, len(result), result[:1000],
                    )
                else:
                    logger.info("[%s] Ollama responded (%d chars)", self.name, len(result))
                return result
            logger.warning("[%s] Unexpected Ollama payload shape; expected 'response' text.", self.name)
            return ""
        except requests.Timeout:
            logger.error(
                "[%s] Ollama timed out after %ss (url=%s). "
                "Increase OLLAMA_TIMEOUT_SECONDS or use a faster model.",
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
        Multi-stage JSON recovery that handles:
        1. Clean JSON (fastest path)
        2. Markdown code fences: ```json ... ``` or ``` ... ```
        3. Inline code fences: `{...}`
        4. JSON object/array embedded in prose
        5. Truncated JSON repair (trailing comma, missing closing brace)
        Returns None only after all recovery attempts fail.
        """
        if not text:
            logger.debug("safe_json_loads: empty input")
            return None

        # Stage 1 — direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Stage 2 — strip markdown triple-fence ```json ... ``` or ``` ... ```
        fence = re.search(r"```(?:json)?\s*\n?([\s\S]*?)```", text, re.IGNORECASE)
        if fence:
            candidate = fence.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
            # still try to extract object/array from inside the fence
            text = candidate  # narrow search scope for stages below

        # Stage 3 — inline single backtick fence `{...}`
        inline = re.search(r"`(\{[\s\S]*?\})`", text)
        if inline:
            try:
                return json.loads(inline.group(1))
            except json.JSONDecodeError:
                pass

        # Stage 4 — extract first complete JSON object {...}
        # Use a greedy search from first { to last } to handle nested objects
        obj_start = text.find("{")
        obj_end = text.rfind("}")
        if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
            candidate = text[obj_start : obj_end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                # Stage 5 — attempt light repair: remove trailing commas before } or ]
                repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
                try:
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    pass

        # Stage 6 — extract first JSON array [...]
        arr_start = text.find("[")
        arr_end = text.rfind("]")
        if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
            candidate = text[arr_start : arr_end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
                try:
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    pass

        logger.warning(
            "safe_json_loads: all recovery stages failed (input len=%d, preview=%r)",
            len(text), text[:150],
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
