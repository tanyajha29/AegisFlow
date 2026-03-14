import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.scan_model import Scan
from ..models.vulnerability_model import Vulnerability
from ..schemas.scan_schema import CodeScanRequest, ScanResult, VulnerabilityOut
from ..services.scan_service import run_scan
from ..services.risk_engine import risk_level
from ..utils.file_handler import save_code_as_file, save_upload_file, cleanup_file


router = APIRouter(prefix="/scan", tags=["scan"])
logger = logging.getLogger("dristi-scan")


def _persist_scan(db: Session, user_id: int, scan_result: dict) -> Scan:
    scan = Scan(
        user_id=user_id,
        file_name=scan_result["file_name"],
        risk_score=scan_result["risk_score"],
        security_score=scan_result["security_score"],
        total_findings=scan_result["total_findings"],
        critical_count=scan_result["critical_count"],
        high_count=scan_result["high_count"],
        medium_count=scan_result["medium_count"],
        low_count=scan_result["low_count"],
        total_issues=scan_result["total_findings"],
        vulnerability_snapshot=scan_result["vulnerabilities"],
    )
    db.add(scan)
    db.flush()

    for finding in scan_result["vulnerabilities"]:
        vuln = Vulnerability(
            scan_id=scan.id,
            name=finding["name"],
            severity=finding["severity"],
            file_name=finding.get("file_name"),
            line_number=finding.get("line_number"),
            description=finding.get("description") or "",
            remediation=finding.get("remediation") or "",
            cwe_reference=finding.get("cwe_reference"),
            code_snippet=finding.get("code_snippet"),
        )
        db.add(vuln)

    db.commit()
    db.refresh(scan)
    return scan


@router.post("/code", response_model=ScanResult)
def scan_code(
    payload: CodeScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info("Scan request (code) by user=%s for file=%s", current_user.id, payload.file_name)
    file_path = save_code_as_file(payload.code, payload.file_name or "pasted_code.py")
    scan_result = run_scan(file_path.name, payload.code)
    scan = _persist_scan(db, current_user.id, scan_result)
    background_tasks.add_task(cleanup_file, file_path)

    return ScanResult(
        scan_id=scan.id,
        file_name=scan_result["file_name"],
        risk_score=scan_result["risk_score"],
        security_score=scan_result["security_score"],
        total_findings=scan_result["total_findings"],
        total_issues=scan_result["total_findings"],
        critical_count=scan_result["critical_count"],
        high_count=scan_result["high_count"],
        medium_count=scan_result["medium_count"],
        low_count=scan_result["low_count"],
        risk_level=risk_level(scan_result["risk_score"]),
        scan_engine=scan_result["scan_engine"],
        rules_applied=scan_result["rules_applied"],
        summary=scan_result["summary"],
        vulnerabilities=[VulnerabilityOut.from_orm(v) for v in scan.vulnerabilities],
    )


@router.post("/upload", response_model=ScanResult)
def scan_upload(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info("Scan request (upload) by user=%s for file=%s", current_user.id, file.filename)
    file_path, content = save_upload_file(file)
    try:
        decoded = content.decode("utf-8", errors="ignore")
    except Exception as exc:
        cleanup_file(file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to read uploaded file") from exc

    scan_result = run_scan(file_path.name, decoded)
    scan = _persist_scan(db, current_user.id, scan_result)
    background_tasks.add_task(cleanup_file, file_path)

    return ScanResult(
        scan_id=scan.id,
        file_name=scan_result["file_name"],
        risk_score=scan_result["risk_score"],
        security_score=scan_result["security_score"],
        total_findings=scan_result["total_findings"],
        total_issues=scan_result["total_findings"],
        critical_count=scan_result["critical_count"],
        high_count=scan_result["high_count"],
        medium_count=scan_result["medium_count"],
        low_count=scan_result["low_count"],
        risk_level=risk_level(scan_result["risk_score"]),
        scan_engine=scan_result["scan_engine"],
        rules_applied=scan_result["rules_applied"],
        summary=scan_result["summary"],
        vulnerabilities=[VulnerabilityOut.from_orm(v) for v in scan.vulnerabilities],
    )
