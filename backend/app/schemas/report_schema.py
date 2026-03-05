from datetime import datetime
from typing import List
from pydantic import BaseModel

from .scan_schema import VulnerabilityOut


class Report(BaseModel):
    scan_id: int
    file_name: str
    scan_date: datetime
    total_vulnerabilities: int
    risk_score: float
    vulnerabilities: List[VulnerabilityOut]


class ReportHistory(BaseModel):
    reports: List[Report]

