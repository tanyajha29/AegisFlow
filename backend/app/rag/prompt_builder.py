from __future__ import annotations

from typing import List

from .schemas import ExplainRequest, KBEntry

_JSON_ONLY_RULE = (
    "IMPORTANT: Your entire response MUST be a single valid JSON object. "
    "Do NOT include any text, explanation, markdown, or code fences before or after the JSON. "
    "Do NOT wrap the JSON in ```json``` or any other delimiters. "
    "Start your response with { and end with }."
)


def _format_context(contexts: List[KBEntry], max_chars: int = 800) -> str:
    if not contexts:
        return "None."
    lines = []
    for idx, ctx in enumerate(contexts, start=1):
        snippet = ctx.content.strip()
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars] + "..."
        lines.append(f"{idx}. [{ctx.source} / {ctx.title}] {snippet}")
    return "\n".join(lines)


def build_explain_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    context_text = _format_context(contexts)
    return (
        f"{_JSON_ONLY_RULE}\n\n"
        "You are a security analysis assistant for DristiScan.\n"
        "Use ONLY the provided retrieved context to explain the finding.\n"
        "Do not invent facts not supported by the context.\n\n"
        "Finding:\n"
        f"- Type: {finding.type}\n"
        f"- Severity: {finding.severity}\n"
        f"- Language: {finding.language or 'unknown'}\n"
        f"- Framework: {finding.framework or 'unknown'}\n"
        f"- File: {finding.file or 'unknown'}\n"
        f"- Line: {finding.line or 'unknown'}\n"
        f"- Code: {finding.code_snippet or 'N/A'}\n"
        f"- Description: {finding.description or 'N/A'}\n\n"
        "Retrieved Context:\n"
        f"{context_text}\n\n"
        "Return a JSON object with EXACTLY these keys:\n"
        "{\n"
        f'  "finding_id": "{finding.finding_id}",\n'
        '  "title": "short descriptive title",\n'
        '  "summary": "1-2 sentence plain-language summary",\n'
        '  "technical_explanation": "detailed technical explanation grounded in context",\n'
        '  "impact": "what an attacker can achieve",\n'
        '  "exploit_scenario": "concrete step-by-step attack scenario",\n'
        '  "fix_recommendation": "actionable remediation steps",\n'
        '  "secure_example": "short code example of the secure pattern",\n'
        '  "references": [{"label": "CWE-XX or OWASP AXX", "source": "CWE or OWASP"}],\n'
        '  "retrieved_context_count": 0\n'
        "}\n\n"
        "Rules:\n"
        "- references must come ONLY from the retrieved context above\n"
        "- secure_example must match the finding language when possible\n"
        "- keep all string values concise and precise\n"
        "- retrieved_context_count must equal the number of context items used"
    )


def build_fix_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    context_text = _format_context(contexts)
    return (
        f"{_JSON_ONLY_RULE}\n\n"
        "You are a security fix assistant for DristiScan.\n"
        "Use ONLY the provided retrieved context to propose a secure fix.\n"
        "Do not invent facts not supported by the context.\n\n"
        "Finding:\n"
        f"- Type: {finding.type}\n"
        f"- Severity: {finding.severity}\n"
        f"- Language: {finding.language or 'unknown'}\n"
        f"- Framework: {finding.framework or 'unknown'}\n"
        f"- File: {finding.file or 'unknown'}\n"
        f"- Line: {finding.line or 'unknown'}\n"
        f"- Code: {finding.code_snippet or 'N/A'}\n"
        f"- Description: {finding.description or 'N/A'}\n\n"
        "Retrieved Context:\n"
        f"{context_text}\n\n"
        "Return a JSON object with EXACTLY these keys:\n"
        "{\n"
        f'  "finding_id": "{finding.finding_id}",\n'
        '  "title": "Fix for <vulnerability type>",\n'
        '  "fix_summary": "1-2 sentence summary of the fix approach",\n'
        '  "why_this_fix_is_safer": "explanation of why this approach eliminates the vulnerability",\n'
        '  "fixed_code": "the corrected code snippet",\n'
        '  "notes": ["additional note 1", "additional note 2"],\n'
        '  "references": [{"label": "CWE-XX or OWASP AXX", "source": "CWE or OWASP"}],\n'
        '  "retrieved_context_count": 0\n'
        "}\n\n"
        "Rules:\n"
        "- fixed_code must be in the same language as the finding\n"
        "- references must come ONLY from the retrieved context above\n"
        "- notes should be actionable follow-up steps\n"
        "- retrieved_context_count must equal the number of context items used"
    )


# Keep backward-compatible alias used by orchestrator.py
def build_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    return build_explain_prompt(finding, contexts)
