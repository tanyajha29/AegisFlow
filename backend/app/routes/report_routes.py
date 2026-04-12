from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.scan_model import Scan
from ..schemas.report_schema import FullStructuredReportSchema, Report, ReportHistory, ProtectedReportRequest
from ..utils.file_handler import strip_generated_prefix
from ..services.report_service import get_report, get_report_pdf, get_structured_report
from ..services.mfa_service import verify_user_otp
from ..services.risk_engine import risk_level
import logging

logger = logging.getLogger("dristi-scan")


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
    return get_structured_report(db, scan_id, user_id=current_user.id)


@router.get("/{scan_id}/pdf")
def fetch_report_pdf(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    otp: str | None = Query(default=None, description="One-time passcode for step-up authentication"),
    otp_header: str | None = Header(default=None, alias="X-OTP"),
):
    if current_user.mfa_enabled:
        otp_value = otp or otp_header
        if not otp_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OTP required to access this report",
            )
        verify_user_otp(db, current_user, otp_value)
    report = get_report(db, scan_id, user_id=current_user.id)
    pdf_bytes = get_report_pdf(db, scan_id, user_id=current_user.id)
    filename = f"DristiScan_Report_{report.file_name}_{report.scan_date.strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )


@router.post("/{scan_id}/protected-pdf")
def download_protected_report(
    scan_id: int,
    payload: ProtectedReportRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not payload.passphrase or len(payload.passphrase) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passphrase is required")

    # ownership enforcement
    report = get_report(db, scan_id, user_id=current_user.id)
    logger.info("Protected report download requested: scan=%s user=%s", scan_id, current_user.id)

    # generate base PDF
    pdf_bytes = get_report_pdf(db, scan_id, user_id=current_user.id)

    # protect PDF using passphrase (PyPDF2 user password)
    try:
        from PyPDF2 import PdfReader, PdfWriter
        import io
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(user_password=payload.passphrase, owner_password=None)
        out_buf = io.BytesIO()
        writer.write(out_buf)
        protected_bytes = out_buf.getvalue()
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Protected PDF generation failed for scan %s: %s", scan_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not protect report")

    filename = f"DristiScan_Report_{report.file_name}_{report.scan_date.strftime('%Y%m%d')}_protected.pdf"
    return StreamingResponse(
        iter([protected_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )
