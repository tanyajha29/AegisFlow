from datetime import datetime
from typing import List
from pydantic import BaseModel

from .scan_schema import VulnerabilityOut


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
