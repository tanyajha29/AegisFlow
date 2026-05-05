from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional

import requests

from app.agents.schemas import AgentResult

logger = logging.getLogger(__name__)
_HTTP_SESSION = requests.Session()

DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL = "openrouter/auto"
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_TEMPERATURE = 0

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_ENDPOINT = f"{OPENROUTER_BASE_URL}/chat/completions"

STRICT_JSON_SYSTEM_PROMPT = (
    "You are a security analysis assistant for DristiScan. "
    "Return ONLY valid JSON. "
    "Do NOT include markdown. "
    "Do NOT include code blocks or backticks. "
    "Do NOT include explanations or prose outside the JSON. "
    "Do NOT include any text before { or after }. "
    "If unsure about a field, return an empty string for that field."
)


def _resolve_model() -> str:
    return (os.getenv("LLM_MODEL") or os.getenv("OLLAMA_MODEL") or DEFAULT_MODEL).strip()


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


def _resolve_max_tokens() -> Optional[int]:
    val = os.getenv("LLM_MAX_TOKENS")
    if not val:
        return None
    try:
        parsed = int(val)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


class BaseAgent:
    """
    LLM caller that routes to OpenRouter (default) or Ollama (legacy fallback).
    """

    def __init__(
        self,
        name: Optional[str] = None,
        system_instructions: Optional[str] = None,
        model: Optional[str] = None,
        url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.name = name or "Base Agent"
        self.system_instructions = (system_instructions or "").strip()
        self.model = (model or _resolve_model()).strip()
        self.timeout = timeout_seconds or _resolve_timeout()
        self.temperature = _resolve_temperature() if temperature is None else float(temperature)
        self.max_tokens = _resolve_max_tokens() if max_tokens is None else max_tokens
        self._debug = os.getenv("RAG_DEBUG", "false").lower() in ("1", "true", "yes")

        self._provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).lower().strip()
        self._api_key = os.getenv("OPENROUTER_API_KEY", "")
        self._site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173")
        self._site_name = os.getenv("OPENROUTER_SITE_NAME", "DristiScan")

        raw_ollama = url or os.getenv("OLLAMA_URL") or "http://localhost:11434"
        self._ollama_url = self._normalize_ollama_url(raw_ollama)

        logger.info(
            "[%s] Initialized - provider=%s model=%s timeout=%ss max_tokens=%s",
            self.name,
            self._provider,
            self.model,
            self.timeout,
            self.max_tokens,
        )

    def send_prompt(self, prompt: str) -> str:
        if self._provider == "ollama":
            return self._send_ollama(prompt)
        return self._send_openrouter(prompt)

    def _send_openrouter(self, prompt: str) -> str:
        if not self._api_key:
            logger.error(
                "[%s] OPENROUTER_API_KEY is not set. Set it in .env or docker-compose environment.",
                self.name,
            )
            return ""

        system_content = STRICT_JSON_SYSTEM_PROMPT
        if self.system_instructions:
            system_content = f"{STRICT_JSON_SYSTEM_PROMPT}\n\n{self.system_instructions}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._site_url,
            "X-Title": self._site_name,
        }

        if self._debug:
            logger.debug(
                "[%s] OpenRouter request model=%s url=%s prompt_len=%d",
                self.name,
                self.model,
                OPENROUTER_ENDPOINT,
                len(prompt),
            )
        else:
            logger.info("[%s] Calling OpenRouter model=%s timeout=%ss", self.name, self.model, self.timeout)

        try:
            resp = _HTTP_SESSION.post(
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
                self.name,
                exc.response.status_code if exc.response else "?",
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

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            logger.warning("[%s] Unexpected OpenRouter response shape: %s", self.name, str(data)[:200])
            return ""

        if not isinstance(content, str):
            logger.warning("[%s] OpenRouter content is not a string: %r", self.name, content)
            return ""

        result = content.strip()
        if self._debug:
            logger.debug("[%s] OpenRouter response_len=%d", self.name, len(result))
        else:
            logger.info("[%s] OpenRouter responded (%d chars)", self.name, len(result))
        return result

    def _send_ollama(self, prompt: str) -> str:
        if self._debug:
            logger.debug(
                "[%s] Ollama request model=%s url=%s prompt_len=%d",
                self.name,
                self.model,
                self._ollama_url,
                len(prompt),
            )
        else:
            logger.info("[%s] Calling Ollama model=%s timeout=%ss", self.name, self.model, self.timeout)

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": self.temperature},
        }
        if self.max_tokens is not None:
            payload["options"]["num_predict"] = self.max_tokens

        try:
            resp = _HTTP_SESSION.post(self._ollama_url, json=payload, timeout=self.timeout)
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
            logger.debug("[%s] Ollama response_len=%d", self.name, len(result))
        else:
            logger.info("[%s] Ollama responded (%d chars)", self.name, len(result))
        return result

    @staticmethod
    def safe_json_loads(text: str) -> Any:
        if not text:
            logger.debug("safe_json_loads: empty input")
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        fence = re.search(r"```(?:json)?\s*\n?([\s\S]*?)```", text, re.IGNORECASE)
        if fence:
            candidate = fence.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                text = candidate

        inline = re.search(r"`(\{[\s\S]*?\})`", text)
        if inline:
            try:
                return json.loads(inline.group(1))
            except json.JSONDecodeError:
                pass

        obj_start = text.find("{")
        obj_end = text.rfind("}")
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

        arr_start = text.find("[")
        arr_end = text.rfind("]")
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
            len(text),
            text[:150],
        )
        return None

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
        raw = self.send_prompt(prompt)
        parsed = self.safe_json_loads(raw)
        if parsed is None:
            return AgentResult(agent=self.name, findings=[], logs=[f"[{self.name}] Invalid or empty response."])
        try:
            result = AgentResult.model_validate(parsed)
        except Exception as exc:
            logger.warning("Agent %s returned invalid payload: %s", self.name, exc)
            return AgentResult(
                agent=self.name,
                findings=[],
                logs=[f"[{self.name}] Invalid response ignored: {exc}"],
            )
        if not result.agent:
            result.agent = self.name
        return result


class TestEchoAgent(BaseAgent):
    def analyze(self, text: str) -> list[dict[str, Any]]:
        raw = self.send_prompt(f"Echo back an empty JSON array. Input length: {len(text)}")
        parsed = self.safe_json_loads(raw)
        return self.ensure_list_of_dicts(parsed)
