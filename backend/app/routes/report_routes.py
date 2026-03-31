from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.scan_model import Scan
from ..schemas.report_schema import FullStructuredReportSchema, Report, ReportHistory
from ..utils.file_handler import strip_generated_prefix
from ..services.report_service import get_report, get_report_pdf, get_structured_report
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
            display_file_name=strip_generated_prefix(s.file_name),
            scan_date=s.scan_date,
            total_vulnerabilities=s.total_findings,
            risk_score=s.risk_score,
            security_score=s.security_score,
            critical_count=s.critical_count,
            high_count=s.high_count,
            medium_count=s.medium_count,
            low_count=s.low_count,
            risk_level=risk_level(s.risk_score),
            vulnerabilities=list(s.vulnerabilities),
        )
        for s in scans
    ]
    return ReportHistory(reports=reports)


@router.get("/{scan_id}", response_model=FullStructuredReportSchema)
def fetch_report(scan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_structured_report(db, scan_id)


@router.get("/{scan_id}/pdf")
def fetch_report_pdf(scan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    report = get_report(db, scan_id)
    pdf_bytes = get_report_pdf(db, scan_id)
    filename = f"DristiScan_Report_{report.file_name}_{report.scan_date.strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )
