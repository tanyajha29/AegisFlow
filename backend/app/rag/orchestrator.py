from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from app.agents.base_agent import BaseAgent
from app.config import get_settings

from .kb_loader import load_kb
from .prompt_builder import build_prompt
from .retriever import retrieve
from .schemas import ExplainRequest, ExplainResponse, KBEntry, Reference

logger = logging.getLogger(__name__)
settings = get_settings()

_agent = BaseAgent(name="RAG Explain Agent")


def _references_from_contexts(contexts: List[KBEntry]) -> List[Reference]:
    refs: List[Reference] = []
    for ctx in contexts:
        refs.append(Reference(label=ctx.title, source=ctx.source))
        for ref in ctx.references:
            refs.append(ref)
    # dedupe by (label, source)
    seen = set()
    deduped: List[Reference] = []
    for ref in refs:
        key = (ref.label, ref.source)
        if key not in seen:
            seen.add(key)
            deduped.append(ref)
    return deduped


def _fallback_by_type(vuln_type: str) -> dict:
    vt = (vuln_type or "").lower()
    if "sql" in vt:
        return {
            "summary": "SQL injection lets attackers modify queries by injecting untrusted input.",
            "technical_explanation": "User-controlled data is concatenated into a SQL statement without parameterization.",
            "impact": "Unauthorized data access, modification, or database takeover.",
            "exploit_scenario": "Attacker supplies ' OR 1=1 -- to bypass authentication and dump user records.",
            "fix_recommendation": "Use parameterized queries/prepared statements and input validation.",
            "secure_example": "cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))",
            "references": [Reference(label="CWE-89", source="CWE"), Reference(label="OWASP A03:2021 Injection", source="OWASP")],
        }
    if "command" in vt:
        return {
            "summary": "Command injection allows execution of arbitrary OS commands.",
            "technical_explanation": "Untrusted input is interpolated into shell commands without sanitization.",
            "impact": "Remote code execution, data exfiltration, or lateral movement.",
            "exploit_scenario": "User supplies ; rm -rf /tmp/data to delete files on the server.",
            "fix_recommendation": "Avoid shell concatenation; use safe process APIs and strict allowlists.",
            "secure_example": "subprocess.run(['ls', safe_path], check=True)",
            "references": [Reference(label="CWE-78", source="CWE")],
        }
    if "xss" in vt:
        return {
            "summary": "Cross-Site Scripting lets attackers run scripts in users' browsers.",
            "technical_explanation": "Unescaped user input is reflected into HTML/JS output.",
            "impact": "Session theft, credential harvesting, defacement.",
            "exploit_scenario": "<script>alert('pwned')</script> is rendered to victims.",
            "fix_recommendation": "Contextual output encoding and input validation; use CSP.",
            "secure_example": "Use templating auto-escape or frameworks' safe rendering helpers.",
            "references": [Reference(label="OWASP A03:2021 Injection", source="OWASP"), Reference(label="CWE-79", source="CWE")],
        }
    if "secret" in vt or "credential" in vt:
        return {
            "summary": "Hardcoded secrets expose credentials in code repositories.",
            "technical_explanation": "Keys/passwords are stored in source and can leak via VCS or logs.",
            "impact": "Unauthorized access to services, data breaches.",
            "exploit_scenario": "Leaked API key allows attackers to use third-party APIs or cloud resources.",
            "fix_recommendation": "Move secrets to a secret manager or environment variables; rotate immediately.",
            "secure_example": "api_key = os.getenv('SERVICE_API_KEY')",
            "references": [Reference(label="CWE-798", source="CWE")],
        }
    if "path" in vt:
        return {
            "summary": "Path traversal lets attackers access unintended files.",
            "technical_explanation": "User input is used in file paths without normalization/allowlisting.",
            "impact": "Disclosure of config/keys or code execution if writable directories are abused.",
            "exploit_scenario": "Supplying ../../etc/passwd to read sensitive files.",
            "fix_recommendation": "Normalize paths, use allowlists, and avoid joining raw user input.",
            "secure_example": "safe_base = Path('/app/data'); safe_path = safe_base / filename; safe_path.resolve().relative_to(safe_base)",
            "references": [Reference(label="CWE-22", source="CWE")],
        }
    return {
        "summary": "The finding indicates a potential security weakness in the application.",
        "technical_explanation": "Untrusted input or insecure patterns may allow abuse.",
        "impact": "Risk ranges from data exposure to code execution depending on context.",
        "exploit_scenario": "An attacker crafts input that abuses the insecure pattern to gain advantage.",
        "fix_recommendation": "Apply least privilege, validate/encode input, and follow secure coding practices.",
        "secure_example": "Apply framework-safe APIs and input validation helpers.",
        "references": [],
    }


def _normalize_response(
    payload: dict,
    req: ExplainRequest,
    default_refs: List[Reference],
    ctx_count: int,
    fallback_defaults: dict,
) -> ExplainResponse:
    def s(key: str, default_key: str) -> str:
        value = payload.get(key, "")
        if value is None or str(value).strip() == "":
            return fallback_defaults.get(default_key, "")
        return str(value).strip()

    raw_refs = payload.get("references") if isinstance(payload, dict) else None
    refs: List[Reference] = []
    if isinstance(raw_refs, list):
        for item in raw_refs:
            if isinstance(item, dict) and item.get("label") and item.get("source"):
                refs.append(Reference(label=str(item["label"]), source=str(item["source"])))
    if not refs:
        refs = default_refs

    return ExplainResponse(
        finding_id=req.finding_id,
        title=s("title", "title") or f"{req.type} in {req.file or 'target'}",
        summary=s("summary", "summary"),
        technical_explanation=s("technical_explanation", "technical_explanation"),
        impact=s("impact", "impact"),
        exploit_scenario=s("exploit_scenario", "exploit_scenario"),
        fix_recommendation=s("fix_recommendation", "fix_recommendation"),
        secure_example=s("secure_example", "secure_example"),
        references=refs,
        retrieved_context_count=ctx_count,
    )


def explain_finding(req: ExplainRequest) -> ExplainResponse:
    kb_entries = load_kb(settings.rag_kb_path)
    contexts = retrieve(req, kb_entries, top_k=settings.rag_top_k) if kb_entries else []
    ctx_refs = _references_from_contexts(contexts)
    ctx_count = len(contexts)
    fallback_defaults = _fallback_by_type(req.type)

    prompt = build_prompt(req, contexts[:3])
    try:
        raw = _agent.send_prompt(prompt)
        parsed = _agent.safe_json_loads(raw)
        if parsed:
            return _normalize_response(parsed, req, ctx_refs, ctx_count, fallback_defaults)
        raise ValueError("Empty or invalid AI response")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("RAG explain fallback due to error: %s", exc)
        fallback = fallback_defaults
        # merge fallback with context references
        if ctx_refs and not fallback["references"]:
            fallback["references"] = ctx_refs
        return ExplainResponse(
            finding_id=req.finding_id,
            title=f"{req.type} in {req.file or 'target'}",
            summary=fallback["summary"],
            technical_explanation=fallback["technical_explanation"],
            impact=fallback["impact"],
            exploit_scenario=fallback["exploit_scenario"],
            fix_recommendation=fallback["fix_recommendation"],
            secure_example=fallback["secure_example"],
            references=fallback["references"] or ctx_refs,
            retrieved_context_count=ctx_count,
        )
