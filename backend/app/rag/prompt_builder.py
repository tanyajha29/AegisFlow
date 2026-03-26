from __future__ import annotations

from typing import List

from .schemas import ExplainRequest, KBEntry

# Prepended to every RAG prompt. Tested against qwen2.5-coder and llama3.1.
_SYSTEM_HEADER = """\
You are a security analysis assistant. You MUST respond with ONLY a valid JSON object.
STRICT RULES — violation will break the system:
- Output ONLY the JSON object, nothing else
- Do NOT write any text before the opening {
- Do NOT write any text after the closing }
- Do NOT use markdown, code fences, or backticks
- Do NOT add explanations, comments, or apologies
- Every string value must be on one line (no raw newlines inside strings — use \\n)
- The response must be parseable by Python json.loads() with zero modification\
"""


def _format_context(contexts: List[KBEntry], max_chars: int = 600) -> str:
    if not contexts:
        return "No context available."
    lines = []
    for idx, ctx in enumerate(contexts, start=1):
        snippet = ctx.content.strip().replace("\n", " ")
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars] + "..."
        lines.append(f"{idx}. [{ctx.source}] {ctx.title}: {snippet}")
    return "\n".join(lines)


def build_explain_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    ctx_count = len(contexts)
    context_text = _format_context(contexts)

    # Build the exact JSON template with the finding_id pre-filled
    # so the model just needs to fill in the string values.
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
        f'  "references": [{{"label": "FILL", "source": "FILL"}}],\n'
        f'  "retrieved_context_count": {ctx_count}\n'
        "}"
    )

    return (
        f"{_SYSTEM_HEADER}\n\n"
        "FINDING TO ANALYZE:\n"
        f"Type: {finding.type}\n"
        f"Severity: {finding.severity}\n"
        f"Language: {finding.language or 'unknown'}\n"
        f"Framework: {finding.framework or 'unknown'}\n"
        f"File: {finding.file or 'unknown'}, Line: {finding.line or 'unknown'}\n"
        f"Code: {(finding.code_snippet or 'N/A').strip()}\n"
        f"Description: {finding.description or 'N/A'}\n\n"
        "KNOWLEDGE BASE CONTEXT (use ONLY these sources for references):\n"
        f"{context_text}\n\n"
        "Fill in the JSON template below. Replace every FILL value. "
        "Output ONLY the completed JSON, nothing else:\n\n"
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
        f'  "references": [{{"label": "FILL", "source": "FILL"}}],\n'
        f'  "retrieved_context_count": {ctx_count}\n'
        "}"
    )

    return (
        f"{_SYSTEM_HEADER}\n\n"
        "FINDING TO FIX:\n"
        f"Type: {finding.type}\n"
        f"Severity: {finding.severity}\n"
        f"Language: {finding.language or 'unknown'}\n"
        f"Framework: {finding.framework or 'unknown'}\n"
        f"File: {finding.file or 'unknown'}, Line: {finding.line or 'unknown'}\n"
        f"Code: {(finding.code_snippet or 'N/A').strip()}\n"
        f"Description: {finding.description or 'N/A'}\n\n"
        "KNOWLEDGE BASE CONTEXT (use ONLY these sources for references):\n"
        f"{context_text}\n\n"
        "Fill in the JSON template below. Replace every FILL value. "
        "fixed_code must be in the same language as the finding. "
        "Output ONLY the completed JSON, nothing else:\n\n"
        f"{json_template}"
    )


# Backward-compatible alias used by orchestrator.py
def build_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    return build_explain_prompt(finding, contexts)
