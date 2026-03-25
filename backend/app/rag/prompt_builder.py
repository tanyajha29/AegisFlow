from __future__ import annotations

from typing import List

from .schemas import ExplainRequest, KBEntry


def _format_context(contexts: List[KBEntry], max_chars: int = 600) -> str:
    lines = []
    for idx, ctx in enumerate(contexts, start=1):
        snippet = ctx.content.strip()
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars] + "..."
        lines.append(f"{idx}. [{ctx.source} / {ctx.title}] {snippet}")
    return "\n".join(lines) if lines else "None."


def build_prompt(finding: ExplainRequest, contexts: List[KBEntry]) -> str:
    context_text = _format_context(contexts)
    return (
        "You are a security analysis assistant for DristiScan.\n\n"
        "Use ONLY the provided retrieved context to explain the finding.\n"
        "Do not invent facts not supported by the context.\n"
        "Return ONLY valid JSON.\n\n"
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
        "Return JSON with:\n"
        "{\n"
        '  "finding_id": "...",\n'
        '  "title": "...",\n'
        '  "summary": "",\n'
        '  "technical_explanation": "",\n'
        '  "impact": "",\n'
        '  "exploit_scenario": "",\n'
        '  "fix_recommendation": "",\n'
        '  "secure_example": "",\n'
        '  "references": [\n'
        '    {\n'
        '      "label": "",\n'
        '      "source": ""\n'
        "    }\n"
        "  ],\n"
        '  "retrieved_context_count": 0\n'
        "}\n\n"
        "Rules:\n"
        "- no markdown\n"
        "- no prose outside JSON\n"
        "- keep explanations precise\n"
        "- secure_example must be relevant to the finding type and language when possible\n"
        "- references must come only from retrieved context"
    )
