from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


Severity = Literal["Critical", "High", "Medium", "Low"]


class CodeScanRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Raw source code content")
    file_name: Optional[str] = Field(default="pasted_code.py")


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
        orm_mode = True


class ScanResult(BaseModel):
    scan_id: int
    file_name: str
    risk_score: float
    total_issues: int
    vulnerabilities: List[VulnerabilityOut | VulnerabilityBase]


class ScanHistoryItem(BaseModel):
    scan_id: int
    file_name: str
    scan_date: datetime
    risk_score: float
    total_issues: int

    class Config:
        orm_mode = True

