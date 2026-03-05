from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.scan_model import Scan
from ..schemas.report_schema import Report
from ..utils.pdf_generator import generate_pdf
from .risk_engine import risk_level


def get_report(db: Session, scan_id: int) -> Report:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return Report(
        scan_id=scan.id,
        file_name=scan.file_name,
        scan_date=scan.scan_date,
        total_vulnerabilities=scan.total_issues,
        risk_score=scan.risk_score,
        risk_level=risk_level(scan.risk_score),
        vulnerabilities=list(scan.vulnerabilities),
    )


def get_report_pdf(db: Session, scan_id: int) -> bytes:
    report = get_report(db, scan_id)
    return generate_pdf(report)
