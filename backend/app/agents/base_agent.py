from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

import httpx
from pydantic import ValidationError

from app.config import get_settings
from app.agents.schemas import AgentResult

logger = logging.getLogger(__name__)


def _resolve_generate_endpoint(base_url: str) -> str:
    """Return full /api/generate endpoint for Ollama."""
    sanitized = base_url.rstrip("/")
    if sanitized.endswith("/api/generate"):
        return sanitized
    return f"{sanitized}/api/generate"


def _resolve_chat_endpoint(base_url: str) -> str:
    sanitized = base_url.rstrip("/")
    if sanitized.endswith("/api/chat"):
        return sanitized
    return f"{sanitized}/api/chat"


class BaseAgent:
    """Shared Ollama-backed agent helpers."""

    def __init__(self, name: str, system_instructions: str | None = None):
        self.name = name
        self.settings = get_settings()
        self.model = getattr(self.settings, "ollama_model", "deepseek-coder")
        self.timeout = getattr(self.settings, "ollama_timeout_seconds", 15.0)
        base = str(self.settings.ollama_url)
        self.endpoint_generate = _resolve_generate_endpoint(base)
        self.endpoint_chat = _resolve_chat_endpoint(base)
        self.system_instructions = (system_instructions or "").strip()
        self.client = httpx.Client(timeout=self.timeout)

    def build_prompt(self, code_snippet: str, task: str) -> str:
        """Compose a deterministic prompt that demands strict JSON."""
        schema_hint = json.dumps(AgentResult.model_json_schema(), indent=2)
        return (
            f"{self.system_instructions}\n"
            f"Task: {task}\n"
            "Always respond with valid JSON only. Do not include prose, code fences, or comments.\n"
            f"Use this JSON schema (fields are required unless marked optional):\n{schema_hint}\n"
            "Input code/content to analyze:\n"
            f"{code_snippet}\n"
        )

    def _call_ollama(self, prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        logger.debug("Sending prompt to Ollama model=%s endpoint=%s", self.model, self.endpoint_generate)
        try:
            response = self.client.post(self.endpoint_generate, json=payload)
            response.raise_for_status()
            data = response.json()
            text = data.get("response") or data.get("output")
            if not isinstance(text, str):
                raise ValueError("Ollama response did not contain text output")
            return text.strip()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (404, 405):
                raise
            # Fallback to chat API for newer/alternate Ollama builds
            chat_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
            logger.debug("Falling back to chat endpoint=%s", self.endpoint_chat)
            response = self.client.post(self.endpoint_chat, json=chat_payload)
            response.raise_for_status()
            data = response.json()
            text = (
                data.get("message", {}).get("content")
                or data.get("response")
                or data.get("output")
                or ""
            )
            if not isinstance(text, str):
                raise ValueError("Ollama chat response did not contain text output")
            return text.strip()

    @staticmethod
    def _extract_json(text: str) -> Any:
        """Attempt to parse JSON, repairing common LLM wrappers."""
        # direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # fenced blocks ```json ... ```
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.lower().startswith("json"):
                    maybe = part[4:].strip()
                else:
                    maybe = part
                try:
                    return json.loads(maybe)
                except json.JSONDecodeError:
                    continue

        # fallback: find first and last brace
        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            snippet = text[start:end]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass

        raise ValueError("Unable to parse JSON from agent response")

    def parse_response(self, raw_text: str) -> AgentResult:
        """Convert raw LLM output into a validated AgentResult."""
        try:
            parsed = self._extract_json(raw_text)
            return AgentResult.model_validate(parsed)
        except (ValueError, ValidationError) as exc:
            logger.warning("Agent %s returned invalid JSON: %s", self.name, exc)
            return AgentResult(
                agent=self.name,
                findings=[],
                logs=[f"[{self.name}] Invalid response ignored: {exc}"],
            )

    def run(self, code_snippet: str, task: str, instructions: Optional[str] = None) -> AgentResult:
        """Invoke Ollama and return a validated result."""
        prompt = self.build_prompt(code_snippet, task)
        if instructions:
            prompt = instructions.strip() + "\n\n" + prompt
        try:
            raw = self._call_ollama(prompt)
            result = self.parse_response(raw)
            if not result.agent:
                result.agent = self.name
            if not result.logs:
                result.logs = [f"[{self.name}] Completed analysis."]
            return result
        except Exception as exc:
            logger.error("Agent %s failed: %s", self.name, exc)
            return AgentResult(
                agent=self.name,
                findings=[],
                logs=[f"[{self.name}] Error: {exc}"],
            )


class TestEchoAgent(BaseAgent):
    """Minimal agent for phase-1 validation."""

    def __init__(self):
        super().__init__(name="Test Agent", system_instructions="You are a JSON-only security assistant.")

    def analyze(self, code_snippet: str) -> AgentResult:
        task = (
            "Echo back an empty findings list and a short log line summarizing the size of the input. "
            "Use the provided JSON schema strictly."
        )
        return self.run(code_snippet=code_snippet, task=task)


if __name__ == "__main__":
    sample_code = "print('hello world')\n"
    agent = TestEchoAgent()
    output = agent.analyze(sample_code)
    print(output.model_dump_json(indent=2))
