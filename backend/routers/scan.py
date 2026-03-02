from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
import models, schemas, database
from routers.auth import get_current_user

router = APIRouter(prefix="/scans", tags=["scans"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.ScanResponse)
async def upload_code(
    title: str = Form(...),
    file: UploadFile = File(None),
    code_content: str = Form(None),
    filename: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file and not code_content:
        raise HTTPException(status_code=400, detail="Either file or code_content must be provided")

    # Create a Scan record
    new_scan = models.Scan(
        title=title,
        status="pending",
        owner_id=current_user.id
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    # Determine file details
    safe_filename = ""
    file_path = ""
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    scan_dir = os.path.join(UPLOAD_DIR, str(new_scan.id))
    os.makedirs(scan_dir, exist_ok=True)

    try:
        if file:
            safe_filename = file.filename
            file_path = os.path.join(scan_dir, safe_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        else:
            safe_filename = filename if filename else f"snippet_{timestamp}.txt"
            file_path = os.path.join(scan_dir, safe_filename)
            with open(file_path, "w") as f:
                f.write(code_content)
        
        # Here we would trigger the actual background scan task
        # For now, we'll just mark it as processing and return
        # In a real app we would use Celery or BackgroundTasks
        
        # We will implement the scanner logic in the next step
        # By calling a sync/async scan function directly for MVP purposes
        
        new_scan.status = "processing"
        db.commit()
        db.refresh(new_scan)
        
        return new_scan

    except Exception as e:
        new_scan.status = "failed"
        db.commit()
        db.refresh(new_scan)
        raise HTTPException(status_code=500, detail=str(e))
