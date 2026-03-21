from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator


Severity = Literal["Critical", "High", "Medium", "Low", "Info"]


class AgentFinding(BaseModel):
    title: str = Field(..., description="Short name of the issue.")
    severity: Severity = Field(..., description="Severity level for the finding.")
    file: Optional[str] = Field(None, description="File path related to the finding.")
    line: Optional[int] = Field(
        None,
        ge=0,
        description="Line number of the finding if available. Use 0 or null when unknown.",
    )
    description: str = Field(..., description="What the agent observed.")
    remediation: str = Field(..., description="Concrete remediation guidance.")
    confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Agent confidence (0-1)."
    )
    detected_by: List[str] = Field(
        default_factory=list,
        description="List of agents or scanners that detected this issue.",
    )

    @field_validator("detected_by", mode="before")
    @classmethod
    def _coerce_detected_by(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return list(value)


class AgentResult(BaseModel):
    agent: str = Field(..., description="Name of the agent producing the result.")
    findings: List[AgentFinding] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)

    @classmethod
    def safe_validate(cls, payload: object) -> "AgentResult":
        """Validate payload, raising ValidationError with a consistent message."""
        try:
            return cls.model_validate(payload)
        except ValidationError as exc:
            raise exc


class OrchestrationOutput(BaseModel):
    agents_used: List[str] = Field(default_factory=list, description="Agents that produced results or logs.")
    findings: List[AgentFinding] = Field(default_factory=list, description="Flattened findings from all agents.")
    agent_results: List[AgentResult] = Field(default_factory=list, description="Raw agent results.")
    logs: List[str] = Field(default_factory=list, description="Merged logs from planner and agents.")
