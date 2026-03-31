from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
import os
import models, schemas, database
from routers.auth import get_current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{scan_id}", response_model=schemas.ScanResponse)
def get_json_report(scan_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    scan = db.query(models.Scan).options(joinedload(models.Scan.vulnerabilities)).filter(models.Scan.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")
        
    return scan

@router.get("/{scan_id}/pdf")
def get_pdf_report(scan_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    scan = db.query(models.Scan).options(joinedload(models.Scan.vulnerabilities)).filter(models.Scan.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")
    
    pdf_filename = f"scan_report_{scan_id}.pdf"
    pdf_path = os.path.join("uploads", pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, f"CodeShield Security Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Scan Title: {scan.title}")
    c.drawString(50, height - 100, f"Date: {scan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, height - 120, f"Risk Score: {scan.risk_score}/100")
    c.drawString(50, height - 140, f"Total Vulnerabilities: {len(scan.vulnerabilities)}")
    
    y_pos = height - 180
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "Vulnerabilities Detail:")
    y_pos -= 30
    
    for v in scan.vulnerabilities:
        if y_pos < 100:
            c.showPage()
            y_pos = height - 50
            
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.red if v.severity == "Critical" else colors.orange if v.severity == "High" else colors.blue)
        c.drawString(50, y_pos, f"[{v.severity}] {v.vulnerability_name}")
        y_pos -= 20
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(70, y_pos, f"File: {v.file_name} @ Line {v.line_number}")
        y_pos -= 15
        
        c.drawString(70, y_pos, f"Explanation: {v.explanation[:80]}...")
        y_pos -= 25
        
    c.save()
    
    return FileResponse(path=pdf_path, filename=pdf_filename, media_type='application/pdf')
