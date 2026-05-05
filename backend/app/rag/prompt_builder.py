from __future__ import annotations

from typing import List

from app.config import get_settings

from .schemas import ExplainRequest, KBEntry

settings = get_settings()

_SYSTEM_HEADER = """\
Return only a valid JSON object.
No markdown, no code fences, no prose outside the JSON.
Keep each string on one line and use \\n inside strings when needed.\
"""


def _format_context(contexts: List[KBEntry]) -> str:
    if not contexts:
        return "No context available."

    max_chunk_chars = max(120, settings.rag_prompt_max_chunk_chars)
    max_total_chars = max(max_chunk_chars, settings.rag_prompt_max_total_chars)
    lines = []
    total_chars = 0

    for idx, ctx in enumerate(contexts, start=1):
        snippet = ctx.content.strip().replace("\n", " ")
        if len(snippet) > max_chunk_chars:
            snippet = snippet[:max_chunk_chars].rstrip() + "..."
        line = f"{idx}. [{ctx.source}] {ctx.title}: {snippet}"
        projected = total_chars + len(line)
        if lines and projected > max_total_chars:
            break
        lines.append(line)
        total_chars = projected

    return "\n".join(lines)


def build_explain_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    ctx_count = len(contexts)
    context_text = _format_context(contexts)

    json_template = (
        "{\n"
        f'  "finding_id": "{finding.finding_id}",\n'
        '  "title": "FILL: short title for this vulnerability",\n'
        '  "summary": "FILL: 1-2 sentence plain-language summary",\n'
        '  "technical_explanation": "FILL: technical explanation grounded in context",\n'
        '  "impact": "FILL: what an attacker can achieve",\n'
        '  "exploit_scenario": "FILL: concrete attack scenario",\n'
        '  "fix_recommendation": "FILL: actionable remediation steps",\n'
        '  "secure_example": "FILL: short secure code example",\n'
        '  "references": [{"label": "FILL", "source": "FILL"}],\n'
        f'  "retrieved_context_count": {ctx_count}\n'
        "}"
    )

    return (
        f"{_SYSTEM_HEADER}\n\n"
        "Analyze this finding.\n"
        f"Type: {finding.type}\n"
        f"Severity: {finding.severity}\n"
        f"Language: {finding.language or 'unknown'}\n"
        f"Framework: {finding.framework or 'unknown'}\n"
        f"Location: {finding.file or 'unknown'}:{finding.line or 'unknown'}\n"
        f"Code: {(finding.code_snippet or 'N/A').strip()}\n"
        f"Description: {finding.description or 'N/A'}\n\n"
        "Use only these sources for references:\n"
        f"{context_text}\n\n"
        "Fill every FILL value in this JSON template and return only the completed JSON:\n\n"
        f"{json_template}"
    )


def build_fix_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    ctx_count = len(contexts)
    context_text = _format_context(contexts)

    json_template = (
        "{\n"
        f'  "finding_id": "{finding.finding_id}",\n'
        f'  "title": "Fix for {finding.type}",\n'
        '  "fix_summary": "FILL: 1-2 sentence summary of the fix",\n'
        '  "why_this_fix_is_safer": "FILL: why this eliminates the vulnerability",\n'
        '  "fixed_code": "FILL: corrected code snippet",\n'
        '  "notes": ["FILL: follow-up step 1", "FILL: follow-up step 2"],\n'
        '  "references": [{"label": "FILL", "source": "FILL"}],\n'
        f'  "retrieved_context_count": {ctx_count}\n'
        "}"
    )

    return (
        f"{_SYSTEM_HEADER}\n\n"
        "Fix this finding.\n"
        f"Type: {finding.type}\n"
        f"Severity: {finding.severity}\n"
        f"Language: {finding.language or 'unknown'}\n"
        f"Framework: {finding.framework or 'unknown'}\n"
        f"Location: {finding.file or 'unknown'}:{finding.line or 'unknown'}\n"
        f"Code: {(finding.code_snippet or 'N/A').strip()}\n"
        f"Description: {finding.description or 'N/A'}\n\n"
        "Use only these sources for references:\n"
        f"{context_text}\n\n"
        "Fill every FILL value in this JSON template. fixed_code must stay in the same language. "
        "Return only the completed JSON:\n\n"
        f"{json_template}"
    )


def build_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    return build_explain_prompt(finding, contexts)
