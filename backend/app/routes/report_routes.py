from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.scan_model import Scan
from ..schemas.report_schema import Report, ReportHistory
from ..services.report_service import get_report, get_report_pdf
from ..services.risk_engine import risk_level


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/history", response_model=ReportHistory)
def history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.scan_date.desc())
        .limit(50)
        .all()
    )
    reports = [
        Report(
            scan_id=s.id,
            file_name=s.file_name,
            scan_date=s.scan_date,
            total_vulnerabilities=s.total_issues,
            risk_score=s.risk_score,
            risk_level=risk_level(s.risk_score),
            vulnerabilities=list(s.vulnerabilities),
        )
        for s in scans
    ]
    return ReportHistory(reports=reports)


@router.get("/{scan_id}", response_model=Report)
def fetch_report(scan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_report(db, scan_id)


@router.get("/{scan_id}/pdf")
def fetch_report_pdf(scan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    pdf_bytes = get_report_pdf(db, scan_id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="scan-{scan_id}-report.pdf"'},
    )
