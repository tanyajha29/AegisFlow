from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


Severity = Literal["Critical", "High", "Medium", "Low"]


class CodeScanRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Raw source code content")
    file_name: Optional[str] = Field(default="pasted_code.py")


class RepoScanRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    branch: Optional[str] = Field(default=None, description="Optional branch name (defaults to default branch)")


class DependencyInfo(BaseModel):
    package: str
    version: str | None = None
    file_name: str


class VulnerabilityBase(BaseModel):
    name: str
    severity: Severity
    file_name: str
    line_number: Optional[int]
    description: str
    remediation: str
    cwe_reference: Optional[str] = None
    code_snippet: Optional[str] = None


class VulnerabilityOut(VulnerabilityBase):
    id: int

    class Config:
        from_attributes = True


class ScanSummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    risk_score: float
    security_score: float


class ScanResult(BaseModel):
    scan_id: int
    file_name: str
    display_file_name: str | None = None
    stored_file_name: str | None = None
    original_file_name: str | None = None
    risk_score: float
    security_score: float
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    total_issues: int | None = None
    risk_level: str | None = None
    scan_engine: str | None = None
    rules_applied: int | None = None
    summary: ScanSummary | None = None
    ai_agents_used: list[str] | None = None
    ai_logs: list[str] | None = None
    ai_raw: list[dict] | None = None
    vulnerabilities: List[VulnerabilityOut | VulnerabilityBase]


class ScanHistoryItem(BaseModel):
    scan_id: int
    file_name: str
    display_file_name: str | None = None
    scan_date: datetime
    risk_score: float
    security_score: float | None = None
    total_findings: int | None = None
    total_issues: int

    class Config:
        from_attributes = True
