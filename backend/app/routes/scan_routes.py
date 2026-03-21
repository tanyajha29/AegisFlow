import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks, status
import anyio
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.scan_model import Scan
from ..models.vulnerability_model import Vulnerability
from ..schemas.scan_schema import CodeScanRequest, RepoScanRequest, ScanResult, VulnerabilityOut
from ..services.scan_service import run_scan, get_rule_count
from ..services.github_service import fetch_repository_sources
from ..services.risk_engine import risk_level
from ..utils.file_handler import save_code_as_file, save_upload_file, cleanup_file, strip_generated_prefix


router = APIRouter(prefix="/scan", tags=["scan"])
logger = logging.getLogger("dristi-scan")


def _persist_scan(db: Session, user_id: int, scan_result: dict) -> Scan:
    scan = Scan(
        user_id=user_id,
        file_name=scan_result.get("display_file_name") or scan_result["file_name"],
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


def _build_response(scan: Scan, scan_result: dict) -> ScanResult:
    return ScanResult(
        scan_id=scan.id,
        file_name=scan_result["file_name"],
        display_file_name=scan_result.get("display_file_name") or scan_result["file_name"],
        stored_file_name=scan_result.get("stored_file_name"),
        original_file_name=scan_result.get("original_file_name"),
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
        ai_agents_used=scan_result.get("ai_agents_used", []),
        ai_logs=scan_result.get("ai_logs", []),
        ai_raw=scan_result.get("ai_raw", []),
        vulnerabilities=[VulnerabilityOut.from_orm(v) for v in scan.vulnerabilities],
    )


@router.post("/code", response_model=ScanResult)
def scan_code(
    payload: CodeScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info("Scan request (code) by user=%s for file=%s", current_user.id, payload.file_name)
    file_path = save_code_as_file(payload.code, payload.file_name or "pasted_code.py")
    scan_result = run_scan(file_path.name, payload.code, original_file_name=payload.file_name)
    scan = _persist_scan(db, current_user.id, scan_result)
    background_tasks.add_task(cleanup_file, file_path)

    return _build_response(scan, scan_result)


@router.post("/upload", response_model=ScanResult)
def scan_upload(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info("Scan request (upload) by user=%s for file=%s", current_user.id, file.filename)
    file_path, content, original_name = save_upload_file(file)
    try:
        decoded = content.decode("utf-8", errors="ignore")
    except Exception as exc:
        cleanup_file(file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to read uploaded file") from exc

    scan_result = run_scan(file_path.name, decoded, original_file_name=original_name)
    scan = _persist_scan(db, current_user.id, scan_result)
    background_tasks.add_task(cleanup_file, file_path)

    return _build_response(scan, scan_result)


@router.post("/repo", response_model=ScanResult)
async def scan_repository(
    payload: RepoScanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info("Repository scan requested by user=%s for repo=%s", current_user.id, payload.repo_url)
    try:
        files = await fetch_repository_sources(payload.repo_url)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    all_findings = []
    for path, content in files:
        # run potentially blocking scan in thread to avoid nested event loop issues
        result = await anyio.to_thread.run_sync(run_scan, path, content, strip_generated_prefix(path))
        all_findings.extend(result["vulnerabilities"])

    from ..services.risk_engine import calculate_risk_score
    from collections import Counter

    counts = Counter(v["severity"] for v in all_findings)
    total = len(all_findings)
    risk = int(round(calculate_risk_score([v["severity"] for v in all_findings])) if all_findings else 0)
    aggregated = {
        "file_name": payload.repo_url,
        "display_file_name": payload.repo_url,
        "stored_file_name": payload.repo_url,
        "vulnerabilities": all_findings,
        "total_findings": total,
        "critical_count": counts.get("Critical", 0),
        "high_count": counts.get("High", 0),
        "medium_count": counts.get("Medium", 0),
        "low_count": counts.get("Low", 0),
        "risk_score": risk,
        "security_score": max(0, 100 - risk),
        "scan_engine": "DristiScan Orchestrator v2 (repo)",
        "rules_applied": get_rule_count(),
        "summary": {
            "total": total,
            "critical": counts.get("Critical", 0),
            "high": counts.get("High", 0),
            "medium": counts.get("Medium", 0),
            "low": counts.get("Low", 0),
            "risk_score": risk,
            "security_score": max(0, 100 - risk),
        },
        "ai_agents_used": [],
        "ai_logs": [],
    }
    scan = _persist_scan(db, current_user.id, aggregated)
    return _build_response(scan, aggregated)
