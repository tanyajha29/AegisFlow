from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from .retriever_service import search_chunks
from .schemas import ExplainRequest, ExplainResponse, FixResponse

agent = BaseAgent(name="RAG Agent")


def _format_context(chunks: List[Dict[str, Any]]) -> str:
    lines = []
    for idx, c in enumerate(chunks, 1):
        lines.append(f"{idx}. [{c.get('source')}] {c.get('title')}: {c.get('content')}")
    return "\n".join(lines) if lines else "None."


def _fallback_explain(req: ExplainRequest, chunks: List[Dict[str, Any]]) -> ExplainResponse:
    return ExplainResponse(
        finding_id=req.finding_id,
        title=f"{req.type} in {req.file or 'target'}",
        summary="AI explanation unavailable; showing deterministic summary.",
        technical_explanation="Untrusted input or insecure pattern detected.",
        impact="Potential data exposure or code execution depending on context.",
        exploit_scenario="An attacker crafts input that abuses the vulnerable code path.",
        fix_recommendation="Validate/escape input and use safe APIs (parameterized queries, sandboxed exec, etc.).",
        secure_example="",
        references=[],
        retrieved_context_count=len(chunks),
    )


def _fallback_fix(req: ExplainRequest, chunks: List[Dict[str, Any]]) -> FixResponse:
    return FixResponse(
        finding_id=req.finding_id,
        title=f"Fix for {req.type}",
        fix_summary="Use safe, parameterized, or framework-provided secure APIs.",
        why_this_fix_is_safer="It separates data from execution and enforces validation/escaping.",
        fixed_code="",
        notes=["Review related CWE/OWASP guidance.", "Add unit tests around the fix."],
        references=[],
        retrieved_context_count=len(chunks),
    )


def _build_explain_prompt(req: ExplainRequest, chunks: List[Dict[str, Any]]) -> str:
    return (
        "You are a security assistant. Use ONLY the retrieved context to explain the finding. "
        "Return ONLY valid JSON in the required schema.\n\n"
        f"Finding:\n"
        f"- Type: {req.type}\n"
        f"- Severity: {req.severity}\n"
        f"- Language: {req.language or 'unknown'}\n"
        f"- Framework: {req.framework or 'unknown'}\n"
        f"- File: {req.file or 'unknown'} line {req.line or 'unknown'}\n"
        f"- Code: {req.code_snippet or 'N/A'}\n"
        f"- Description: {req.description or 'N/A'}\n\n"
        "Retrieved Context:\n"
        f"{_format_context(chunks)}\n\n"
        "Return JSON with keys: "
        "finding_id, title, summary, technical_explanation, impact, exploit_scenario, "
        "fix_recommendation, secure_example, references (list of {label, source}), retrieved_context_count."
    )


def _build_fix_prompt(req: ExplainRequest, chunks: List[Dict[str, Any]]) -> str:
    return (
        "You are a security assistant. Use ONLY the retrieved context to propose a secure fix. "
        "Return ONLY valid JSON.\n\n"
        f"Finding:\n"
        f"- Type: {req.type}\n"
        f"- Severity: {req.severity}\n"
        f"- Language: {req.language or 'unknown'}\n"
        f"- Framework: {req.framework or 'unknown'}\n"
        f"- File: {req.file or 'unknown'} line {req.line or 'unknown'}\n"
        f"- Code: {req.code_snippet or 'N/A'}\n"
        f"- Description: {req.description or 'N/A'}\n\n"
        "Retrieved Context:\n"
        f"{_format_context(chunks)}\n\n"
        "Return JSON with keys: finding_id, title, fix_summary, why_this_fix_is_safer, "
        "fixed_code, notes (array), references (list of {label, source}), retrieved_context_count."
    )


def run_explain(db: Session, req: ExplainRequest) -> ExplainResponse:
    chunks = search_chunks(db, req.description or req.type, req.type, req.language, req.framework, top_k=5)
    prompt = _build_explain_prompt(req, chunks)
    try:
        raw = agent.send_prompt(prompt)
        parsed = agent.safe_json_loads(raw)
        if not isinstance(parsed, dict):
            return _fallback_explain(req, chunks)
        parsed["finding_id"] = req.finding_id
        parsed["retrieved_context_count"] = len(chunks)
        return ExplainResponse(**parsed)
    except Exception:
        return _fallback_explain(req, chunks)


def run_fix(db: Session, req: ExplainRequest) -> FixResponse:
    chunks = search_chunks(db, req.description or req.type, req.type, req.language, req.framework, top_k=5)
    prompt = _build_fix_prompt(req, chunks)
    try:
        raw = agent.send_prompt(prompt)
        parsed = agent.safe_json_loads(raw)
        if not isinstance(parsed, dict):
            return _fallback_fix(req, chunks)
        parsed["finding_id"] = req.finding_id
        parsed["retrieved_context_count"] = len(chunks)
        return FixResponse(**parsed)
    except Exception:
        return _fallback_fix(req, chunks)
