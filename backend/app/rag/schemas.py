from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Reference(BaseModel):
    label: str
    source: str


class ExplainRequest(BaseModel):
    finding_id: str
    type: str
    severity: str
    file: Optional[str] = None
    line: Optional[int] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    code_snippet: Optional[str] = None
    description: Optional[str] = None


class ExplainResponse(BaseModel):
    finding_id: str
    title: str
    summary: str
    technical_explanation: str
    impact: str
    exploit_scenario: str
    fix_recommendation: str
    secure_example: str
    references: List[Reference] = Field(default_factory=list)
    retrieved_context_count: int = 0
    source_mode: str = "rag"  # "rag" | "fallback"


class KBEntry(BaseModel):
    id: str
    title: str
    source: str
    vulnerability_type: str
    language: Optional[str] = None
    framework: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    content: str
    references: List[Reference] = Field(default_factory=list)


class FixResponse(BaseModel):
    finding_id: str
    title: str
    fix_summary: str
    why_this_fix_is_safer: str
    fixed_code: str
    notes: List[str] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    retrieved_context_count: int = 0
    source_mode: str = "rag"  # "rag" | "fallback"


class SearchRequest(BaseModel):
    query: str
    vulnerability_type: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    top_k: int = 5


class SearchChunk(BaseModel):
    chunk_id: str
    source: str
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)
    similarity: float


class SearchResponse(BaseModel):
    results: List[SearchChunk]
