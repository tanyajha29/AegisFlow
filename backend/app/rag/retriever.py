from __future__ import annotations

import re
from typing import Iterable, List, Tuple

from .schemas import ExplainRequest, KBEntry


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    return {t for t in re.split(r"[^a-zA-Z0-9_]+", text.lower()) if t}


def _score_entry(finding: ExplainRequest, entry: KBEntry) -> float:
    score = 0.0
    # Type match
    if entry.vulnerability_type.lower() == finding.type.lower():
        score += 5.0
    elif entry.vulnerability_type.lower() in finding.type.lower() or finding.type.lower() in entry.vulnerability_type.lower():
        score += 3.0

    # Language / framework match
    if finding.language and entry.language and finding.language.lower() == entry.language.lower():
        score += 2.0
    if finding.framework and entry.framework and finding.framework.lower() == entry.framework.lower():
        score += 2.0

    # Tag overlap
    find_tags = _tokenize(f"{finding.type} {finding.description or ''}")
    entry_tags = {t.lower() for t in entry.tags}
    score += float(len(find_tags & entry_tags))

    # Keyword overlap with content
    keywords = _tokenize(f"{finding.description or ''} {finding.code_snippet or ''}")
    content_tokens = _tokenize(entry.content)
    overlap = keywords & content_tokens
    score += min(5.0, float(len(overlap))) * 0.5

    return score


def retrieve(findings_req: ExplainRequest, kb_entries: Iterable[KBEntry], top_k: int = 5) -> List[KBEntry]:
    scored: List[Tuple[float, KBEntry]] = []
    for entry in kb_entries:
        scored.append((_score_entry(findings_req, entry), entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for score, entry in scored[:top_k] if score > 0]
