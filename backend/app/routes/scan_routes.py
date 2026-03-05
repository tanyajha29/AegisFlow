import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.scan_model import Scan
from ..models.vulnerability_model import Vulnerability
from ..schemas.scan_schema import CodeScanRequest, ScanResult, VulnerabilityOut
from ..services import scanner_service
from ..services.risk_engine import calculate_risk_score, risk_level
from ..utils.file_handler import save_code_as_file, save_upload_file, cleanup_file


router = APIRouter(prefix="/scan", tags=["scan"])
logger = logging.getLogger("dristi-scan")


def _persist_scan(db: Session, user_id: int, file_name: str, findings: list[dict]) -> Scan:
    scan = Scan(user_id=user_id, file_name=file_name)
    db.add(scan)
    db.flush()

    for finding in findings:
        vuln = Vulnerability(
            scan_id=scan.id,
            name=finding["name"],
            severity=finding["severity"],
            file_name=finding["file_name"],
            line_number=finding.get("line_number"),
            description=finding.get("description", ""),
            remediation=finding.get("remediation", ""),
            cwe_reference=finding.get("cwe_reference"),
            code_snippet=finding.get("code_snippet"),
        )
        db.add(vuln)

    scan.risk_score = calculate_risk_score([f["severity"] for f in findings]) if findings else 100.0
    scan.total_issues = len(findings)
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
    findings = [scanner_service.normalize_vulnerability(v) for v in scanner_service.run_scanners(file_path.name, payload.code)]

    scan = _persist_scan(db, current_user.id, file_path.name, findings)
    background_tasks.add_task(cleanup_file, file_path)

    return ScanResult(
        scan_id=scan.id,
        file_name=scan.file_name,
        risk_score=scan.risk_score,
        total_issues=scan.total_issues,
        risk_level=risk_level(scan.risk_score),
        vulnerabilities=[
            VulnerabilityOut.from_orm(v) if isinstance(v, Vulnerability) else VulnerabilityOut(id=0, **v) for v in scan.vulnerabilities
        ],
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

    findings = [scanner_service.normalize_vulnerability(v) for v in scanner_service.run_scanners(file_path.name, decoded)]
    scan = _persist_scan(db, current_user.id, file_path.name, findings)
    background_tasks.add_task(cleanup_file, file_path)

    return ScanResult(
        scan_id=scan.id,
        file_name=scan.file_name,
        risk_score=scan.risk_score,
        total_issues=scan.total_issues,
        risk_level=risk_level(scan.risk_score),
        vulnerabilities=[
            VulnerabilityOut.from_orm(v) if isinstance(v, Vulnerability) else VulnerabilityOut(id=0, **v) for v in scan.vulnerabilities
        ],
    )
