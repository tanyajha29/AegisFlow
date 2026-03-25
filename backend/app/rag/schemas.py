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
