from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel

from .scan_schema import VulnerabilityOut


RiskLevel = Literal["Critical", "High", "Medium", "Low"]


class ReportSummarySchema(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    overall_risk: RiskLevel


class ReportFindingSchema(BaseModel):
    type: str
    severity: str
    line: int
    code: str
    description: str
    impact: str
    attack_example: str
    recommendation: str
    fix_code: str


class ReportRiskScoreSchema(BaseModel):
    score: float
    reason: str


class ReportInsightsSchema(BaseModel):
    summary: str
    most_critical_issue: str
    fix_priority: str


class FullStructuredReportSchema(BaseModel):
    summary: ReportSummarySchema
    findings: List[ReportFindingSchema]
    risk_score: ReportRiskScoreSchema
    ai_insights: ReportInsightsSchema
    secure_version: str


class Report(BaseModel):
    scan_id: int
    file_name: str
    display_file_name: str | None = None
    scan_date: datetime
    total_vulnerabilities: int
    risk_score: float
    security_score: float | None = None
    critical_count: int | None = None
    high_count: int | None = None
    medium_count: int | None = None
    low_count: int | None = None
    risk_level: str | None = None
    vulnerabilities: List[VulnerabilityOut]

    class Config:
        from_attributes = True


class ReportHistory(BaseModel):
    reports: List[Report]


class ProtectedReportRequest(BaseModel):
    passphrase: str
