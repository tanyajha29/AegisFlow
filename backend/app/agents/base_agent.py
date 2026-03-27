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

# ── defaults ────────────────────────────────────────────────────────────────

DEFAULT_PROVIDER        = "openrouter"
DEFAULT_MODEL           = "openrouter/auto"
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_TEMPERATURE     = 0

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_ENDPOINT = f"{OPENROUTER_BASE_URL}/chat/completions"

# Strict system prompt sent on every OpenRouter call.
# Forces JSON-only output regardless of which free model is selected.
STRICT_JSON_SYSTEM_PROMPT = (
    "You are a security analysis assistant for DristiScan. "
    "Return ONLY valid JSON. "
    "Do NOT include markdown. "
    "Do NOT include code blocks or backticks. "
    "Do NOT include explanations or prose outside the JSON. "
    "Do NOT include any text before { or after }. "
    "If unsure about a field, return an empty string for that field."
)


# ── helpers ─────────────────────────────────────────────────────────────────

def _resolve_model() -> str:
    """
    Priority: LLM_MODEL env var → OLLAMA_MODEL env var (legacy) → default.
    Allows switching models without code changes.
    """
    return (
        os.getenv("LLM_MODEL")
        or os.getenv("OLLAMA_MODEL")
        or DEFAULT_MODEL
    ).strip()


def _resolve_timeout() -> float:
    for key in ("LLM_TIMEOUT_SECONDS", "OLLAMA_TIMEOUT_SECONDS"):
        val = os.getenv(key)
        if val:
            try:
                return float(val)
            except ValueError:
                pass
    return float(DEFAULT_TIMEOUT_SECONDS)


def _resolve_temperature() -> float:
    try:
        return float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))
    except ValueError:
        return float(DEFAULT_TEMPERATURE)


# ── BaseAgent ────────────────────────────────────────────────────────────────

class BaseAgent:
    """
    LLM caller that routes to OpenRouter (default) or Ollama (legacy fallback).

    Provider selection via env var:
      LLM_PROVIDER=openrouter  → uses OpenRouter /chat/completions (default)
      LLM_PROVIDER=ollama      → uses local Ollama /api/generate (legacy)

    Key env vars:
      LLM_PROVIDER            openrouter | ollama
      LLM_MODEL               model identifier (e.g. openrouter/auto)
      LLM_TIMEOUT_SECONDS     request timeout in seconds
      LLM_TEMPERATURE         sampling temperature (0 = deterministic)
      OPENROUTER_API_KEY      required for OpenRouter
      OPENROUTER_SITE_URL     sent as HTTP-Referer header
      OPENROUTER_SITE_NAME    sent as X-Title header
      RAG_DEBUG               true/false — verbose logging
    """

    def __init__(
        self,
        name: Optional[str] = None,
        system_instructions: Optional[str] = None,
        model: Optional[str] = None,
        url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> None:
        self.name = name or "Base Agent"
        self.system_instructions = (system_instructions or "").strip()
        self.model = (model or _resolve_model()).strip()
        self.timeout = timeout_seconds or _resolve_timeout()
        self.temperature = _resolve_temperature()
        self._debug = os.getenv("RAG_DEBUG", "false").lower() in ("1", "true", "yes")

        # Provider routing
        self._provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).lower().strip()

        # OpenRouter config
        self._api_key = os.getenv("OPENROUTER_API_KEY", "")
        self._site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173")
        self._site_name = os.getenv("OPENROUTER_SITE_NAME", "DristiScan")

        # Legacy Ollama config (only used when LLM_PROVIDER=ollama)
        _raw_ollama = url or os.getenv("OLLAMA_URL") or "http://localhost:11434"
        self._ollama_url = self._normalize_ollama_url(_raw_ollama)

        logger.info(
            "[%s] Initialized — provider=%s model=%s timeout=%ss",
            self.name, self._provider, self.model, self.timeout,
        )

    # ── routing ─────────────────────────────────────────────────────────────

    def send_prompt(self, prompt: str) -> str:
        """
        Send a prompt to the configured LLM provider.
        Returns raw text content, or empty string on any failure.
        """
        if self._provider == "ollama":
            return self._send_ollama(prompt)
        return self._send_openrouter(prompt)

    # ── OpenRouter ──────────────────────────────────────────────────────────

    def _send_openrouter(self, prompt: str) -> str:
        if not self._api_key:
            logger.error(
                "[%s] OPENROUTER_API_KEY is not set. "
                "Set it in .env or docker-compose environment.",
                self.name,
            )
            return ""

        # System message: always use STRICT_JSON_SYSTEM_PROMPT.
        # If caller passed extra system_instructions, append them.
        system_content = STRICT_JSON_SYSTEM_PROMPT
        if self.system_instructions:
            system_content = f"{STRICT_JSON_SYSTEM_PROMPT}\n\n{self.system_instructions}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user",   "content": prompt},
            ],
            "temperature": self.temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  self._site_url,
            "X-Title":       self._site_name,
        }

        if self._debug:
            logger.debug(
                "[%s] OpenRouter request — model=%s url=%s\nPrompt preview:\n%s",
                self.name, self.model, OPENROUTER_ENDPOINT, prompt[:600],
            )
        else:
            logger.info("[%s] Calling OpenRouter model=%s timeout=%ss", self.name, self.model, self.timeout)

        try:
            resp = requests.post(
                OPENROUTER_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except requests.Timeout:
            logger.error("[%s] OpenRouter timed out after %ss", self.name, self.timeout)
            return ""
        except requests.ConnectionError as exc:
            logger.error("[%s] OpenRouter connection error: %s", self.name, exc)
            return ""
        except requests.HTTPError as exc:
            logger.error(
                "[%s] OpenRouter HTTP %s: %s",
                self.name, exc.response.status_code if exc.response else "?",
                exc.response.text[:300] if exc.response else str(exc),
            )
            return ""
        except requests.RequestException as exc:
            logger.error("[%s] OpenRouter request failed: %s", self.name, exc)
            return ""

        try:
            data = resp.json()
        except ValueError:
            logger.warning("[%s] OpenRouter response not JSON-decodable", self.name)
            return ""

        # Extract content from choices[0].message.content only.
        # Deliberately ignore reasoning / reasoning_details / other fields.
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            logger.warning(
                "[%s] Unexpected OpenRouter response shape: %s",
                self.name, str(data)[:200],
            )
            return ""

        if not isinstance(content, str):
            logger.warning("[%s] OpenRouter content is not a string: %r", self.name, content)
            return ""

        result = content.strip()
        if self._debug:
            logger.debug("[%s] Raw OpenRouter response (%d chars):\n%s", self.name, len(result), result[:1000])
        else:
            logger.info("[%s] OpenRouter responded (%d chars)", self.name, len(result))

        return result

    # ── Ollama (legacy) ─────────────────────────────────────────────────────

    def _send_ollama(self, prompt: str) -> str:
        if self._debug:
            logger.debug(
                "[%s] Ollama request — model=%s url=%s\nPrompt preview:\n%s",
                self.name, self.model, self._ollama_url, prompt[:600],
            )
        else:
            logger.info("[%s] Calling Ollama model=%s timeout=%ss", self.name, self.model, self.timeout)

        payload = {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}
        try:
            resp = requests.post(self._ollama_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except requests.Timeout:
            logger.error("[%s] Ollama timed out after %ss (url=%s)", self.name, self.timeout, self._ollama_url)
            return ""
        except requests.ConnectionError as exc:
            logger.error("[%s] Ollama connection refused (is Ollama running at %s?): %s", self.name, self._ollama_url, exc)
            return ""
        except requests.RequestException as exc:
            logger.error("[%s] Ollama request failed: %s", self.name, exc)
            return ""

        try:
            data = resp.json()
        except ValueError:
            logger.warning("[%s] Ollama response not JSON-decodable", self.name)
            return ""

        text = data.get("response") or data.get("output") or ""
        if not isinstance(text, str):
            logger.warning("[%s] Unexpected Ollama payload shape", self.name)
            return ""

        result = text.strip()
        if self._debug:
            logger.debug("[%s] Raw Ollama response (%d chars):\n%s", self.name, len(result), result[:1000])
        else:
            logger.info("[%s] Ollama responded (%d chars)", self.name, len(result))
        return result

    # ── JSON parsing ────────────────────────────────────────────────────────

    @staticmethod
    def safe_json_loads(text: str) -> Any:
        """
        6-stage JSON recovery. Handles:
        1. Clean JSON
        2. Markdown triple-fences  ```json ... ```
        3. Inline backtick fence   `{...}`
        4. JSON object embedded in prose  (first { … last })
        5. Trailing-comma repair
        6. JSON array embedded in prose   (first [ … last ])
        Returns None only after all stages fail.
        """
        if not text:
            logger.debug("safe_json_loads: empty input")
            return None

        # Stage 1
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Stage 2 — triple fence
        fence = re.search(r"```(?:json)?\s*\n?([\s\S]*?)```", text, re.IGNORECASE)
        if fence:
            candidate = fence.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                text = candidate  # narrow scope for later stages

        # Stage 3 — inline backtick
        inline = re.search(r"`(\{[\s\S]*?\})`", text)
        if inline:
            try:
                return json.loads(inline.group(1))
            except json.JSONDecodeError:
                pass

        # Stage 4 + 5 — first { … last }
        obj_start = text.find("{")
        obj_end   = text.rfind("}")
        if obj_start != -1 and obj_end > obj_start:
            candidate = text[obj_start : obj_end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
                try:
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    pass

        # Stage 6 — first [ … last ]
        arr_start = text.find("[")
        arr_end   = text.rfind("]")
        if arr_start != -1 and arr_end > arr_start:
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
            "safe_json_loads: all 6 recovery stages failed (len=%d, preview=%r)",
            len(text), text[:150],
        )
        return None

    # ── utilities ────────────────────────────────────────────────────────────

    @staticmethod
    def ensure_list_of_dicts(payload: Any) -> list[dict[str, Any]]:
        if not payload:
            return []
        if isinstance(payload, dict):
            return [payload]
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    @staticmethod
    def _normalize_ollama_url(url: str) -> str:
        cleaned = (url or "").rstrip("/")
        if cleaned.endswith("/api/generate"):
            return cleaned
        if cleaned.endswith("/api"):
            return f"{cleaned}/generate"
        return f"{cleaned}/api/generate" if cleaned else "http://localhost:11434/api/generate"

    # ── backwards-compatible runner ──────────────────────────────────────────

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
        prompt = self.build_prompt(code_snippet, task, instructions)
        raw    = self.send_prompt(prompt)
        parsed = self.safe_json_loads(raw)
        if parsed is None:
            return AgentResult(
                agent=self.name, findings=[], logs=[f"[{self.name}] Invalid or empty response."]
            )
        try:
            result = AgentResult.model_validate(parsed)
        except Exception as exc:
            logger.warning("Agent %s returned invalid payload: %s", self.name, exc)
            return AgentResult(
                agent=self.name, findings=[], logs=[f"[{self.name}] Invalid response ignored: {exc}"]
            )
        if not result.agent:
            result.agent = self.name
        return result


# Backwards compatibility
class TestEchoAgent(BaseAgent):
    def analyze(self, text: str) -> list[dict[str, Any]]:
        raw    = self.send_prompt(f"Echo back an empty JSON array. Input length: {len(text)}")
        parsed = self.safe_json_loads(raw)
        return self.ensure_list_of_dicts(parsed)
