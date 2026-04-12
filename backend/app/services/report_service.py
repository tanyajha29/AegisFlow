"""DristiScan PDF Report Generator — professional enterprise layout."""
from __future__ import annotations
import logging
import os
from collections import Counter
from datetime import datetime
from io import BytesIO
from typing import List
from xml.sax.saxutils import escape
from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.utils import ImageReader
from sqlalchemy.orm import Session
from ..models.scan_model import Scan
from ..schemas.report_schema import FullStructuredReportSchema, Report
from ..config import get_settings
from .risk_engine import risk_level
from .structured_report import build_structured_report

logger = logging.getLogger("dristi-scan")
settings = get_settings()

PW, PH = A4
ML, MR, MT, MB = 20*mm, 20*mm, 22*mm, 22*mm
CONTENT_W = PW - ML - MR

C_NAVY=colors.HexColor("#0a1628"); C_NAVY2=colors.HexColor("#0f2040")
C_CYAN=colors.HexColor("#06b6d4"); C_CYAN_DARK=colors.HexColor("#0e7490")
C_WHITE=colors.white; C_OFFWHITE=colors.HexColor("#f8fafc")
C_SLATE=colors.HexColor("#64748b"); C_SLATE_LT=colors.HexColor("#cbd5e1")
C_TEXT=colors.HexColor("#1e293b"); C_MUTED=colors.HexColor("#94a3b8")
C_RULE=colors.HexColor("#e2e8f0")
SEV_COLORS={"Critical":colors.HexColor("#dc2626"),"High":colors.HexColor("#ea580c"),
            "Medium":colors.HexColor("#ca8a04"),"Low":colors.HexColor("#16a34a")}
SEV_BG={"Critical":colors.HexColor("#fef2f2"),"High":colors.HexColor("#fff7ed"),
        "Medium":colors.HexColor("#fefce8"),"Low":colors.HexColor("#f0fdf4")}
THEME_BG=C_WHITE  # kept for any legacy callers



_STYLES_CACHE = None
def _styles():
    global _STYLES_CACHE
    if _STYLES_CACHE:
        return _STYLES_CACHE
    b = getSampleStyleSheet()
    def a(n, **kw):
        if n not in b: b.add(ParagraphStyle(name=n, **kw))
        return b[n]
    a("DS_Cover_Brand",fontSize=28,leading=34,textColor=C_NAVY2,fontName="Helvetica-Bold",alignment=TA_CENTER)
    a("DS_Cover_Tag",fontSize=11,leading=15,textColor=C_SLATE,fontName="Helvetica",alignment=TA_CENTER,spaceAfter=6)
    a("DS_Cover_Title",fontSize=18,leading=24,textColor=C_NAVY,fontName="Helvetica-Bold",alignment=TA_CENTER,spaceBefore=12,spaceAfter=6)
    a("DS_Cover_Sub",fontSize=11,leading=15,textColor=C_SLATE,fontName="Helvetica",alignment=TA_CENTER,spaceAfter=4)
    a("DS_H1",fontSize=15,leading=20,textColor=C_NAVY,fontName="Helvetica-Bold",spaceBefore=14,spaceAfter=6)
    a("DS_H2",fontSize=12,leading=16,textColor=C_NAVY2,fontName="Helvetica-Bold",spaceBefore=10,spaceAfter=4)
    a("DS_Body",fontSize=9,leading=13,textColor=C_TEXT,fontName="Helvetica",spaceAfter=4)
    a("DS_BodySmall",fontSize=8,leading=12,textColor=C_SLATE,fontName="Helvetica",spaceAfter=2)
    a("DS_Code",fontSize=7.5,leading=11,textColor=C_TEXT,fontName="Courier",spaceAfter=4,leftIndent=4,rightIndent=4)
    a("DS_TOC_Entry",fontSize=9,leading=14,textColor=C_TEXT,fontName="Helvetica",spaceAfter=2)
    a("DS_Label",fontSize=7,leading=10,textColor=C_MUTED,fontName="Helvetica-Bold",spaceAfter=1)
    _STYLES_CACHE = b
    return b

def _rule(color=None,thickness=0.5):
    return HRFlowable(width="100%",thickness=thickness,color=color or C_RULE,spaceAfter=6,spaceBefore=2)
def _sp(h=6): return Spacer(1,h)
def _safe(t): return escape(str(t or ""))

def _code_block(code):
    st=_styles()
    lines=str(code or "").strip().splitlines()[:40]
    cell=Paragraph(_safe("\n".join(lines)),st["DS_Code"])
    t=Table([[cell]],colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f1f5f9")),
                            ("BOX",(0,0),(-1,-1),0.5,C_SLATE_LT),("TOPPADDING",(0,0),(-1,-1),6),
                            ("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8),
                            ("RIGHTPADDING",(0,0),(-1,-1),8)]))
    return t

def _info_table(rows):
    st=_styles(); w2=CONTENT_W-55*mm
    data=[[Paragraph(_safe(k),st["DS_Label"]),Paragraph(_safe(v),st["DS_Body"])] for k,v in rows]
    t=Table(data,colWidths=[55*mm,w2])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),4),
                            ("BOTTOMPADDING",(0,0),(-1,-1),4),("LEFTPADDING",(0,0),(-1,-1),0),
                            ("RIGHTPADDING",(0,0),(-1,-1),6),("LINEBELOW",(0,0),(-1,-2),0.25,C_RULE)]))
    return t

def _section_header(title,number=""):
    st=_styles(); label=f"{number}  {title}" if number else title
    return [_rule(C_CYAN,1.5),Paragraph(label,st["DS_H1"]),_sp(4)]

def _draw_logo(canvas, path: str | None, x: float, y: float, target_width_mm: float = 24):
    if not path or not os.path.exists(path):
        return
    try:
        img = ImageReader(path)
        iw, ih = img.getSize()
        width = target_width_mm * mm
        height = width * (ih / iw) if iw else target_width_mm * mm
        canvas.drawImage(img, x, y - height, width=width, height=height, mask="auto", preserveAspectRatio=True)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Could not render logo on PDF header: %s", exc)

def _sev_count_table(critical,high,medium,low):
    cw=CONTENT_W/4
    hs=ParagraphStyle("SCH",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
    vs=ParagraphStyle("SCV",fontSize=20,leading=24,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
    data=[[Paragraph("CRITICAL",hs),Paragraph("HIGH",hs),Paragraph("MEDIUM",hs),Paragraph("LOW",hs)],
          [Paragraph(str(critical),vs),Paragraph(str(high),vs),Paragraph(str(medium),vs),Paragraph(str(low),vs)]]
    t=Table(data,colWidths=[cw,cw,cw,cw])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),SEV_COLORS["Critical"]),
                            ("BACKGROUND",(1,0),(1,-1),SEV_COLORS["High"]),
                            ("BACKGROUND",(2,0),(2,-1),SEV_COLORS["Medium"]),
                            ("BACKGROUND",(3,0),(3,-1),SEV_COLORS["Low"]),
                            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                            ("LINEAFTER",(0,0),(2,-1),0.5,C_WHITE)]))
    return t



class _DSDocTemplate(BaseDocTemplate):
    def __init__(self,buffer,scan_id,file_name,logo_path=None,**kw):
        super().__init__(buffer,**kw)
        self._scan_id=scan_id; self._file_name=file_name; self._logo_path=logo_path
        cf=Frame(ML,MB,CONTENT_W,PH-MT-MB,id="cover")
        inf=Frame(ML,MB+10*mm,CONTENT_W,PH-MT-MB-10*mm,id="inner")
        self.addPageTemplates([PageTemplate(id="Cover",frames=[cf],onPage=self._on_cover),
                               PageTemplate(id="Inner",frames=[inf],onPage=self._on_inner)])
    def _on_cover(self,canvas,doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE); canvas.rect(0,0,PW,PH,fill=1,stroke=0)
        canvas.setStrokeColor(C_RULE); canvas.setLineWidth(0.5)
        canvas.line(ML,PH-18*mm,PW-MR,PH-18*mm)
        canvas.restoreState()
    def _on_inner(self,canvas,doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE); canvas.rect(0,0,PW,PH,fill=1,stroke=0)
        _draw_logo(canvas,self._logo_path,ML,PH-10*mm,22)
        canvas.setFont("Helvetica-Bold",9); canvas.setFillColor(C_NAVY2)
        canvas.drawString(ML+25*mm,PH-10*mm,"DristiScan")
        canvas.setFont("Helvetica",7); canvas.setFillColor(C_SLATE)
        canvas.drawRightString(PW-MR,PH-10*mm,(self._file_name or "")[:70])
        canvas.setStrokeColor(C_RULE); canvas.setLineWidth(0.6)
        canvas.line(ML,PH-14*mm,PW-MR,PH-14*mm)
        canvas.line(ML,MB+8*mm,PW-MR,MB+8*mm)
        canvas.setFont("Helvetica",7); canvas.setFillColor(C_MUTED)
        canvas.drawString(ML,MB+4*mm,f"Confidential – DristiScan  ·  Scan #{self._scan_id}")
        canvas.drawRightString(PW-MR,MB+4*mm,f"Page {doc.page}")
        canvas.restoreState()



def _cover_page(scan,structured,logo_path: str | None):
    st=_styles(); s=structured.summary
    risk_label=s.overall_risk; risk_color=SEV_COLORS.get(risk_label,C_SLATE)
    scan_date=getattr(scan,"scan_date",datetime.utcnow())
    date_str=scan_date.strftime("%B %d, %Y") if hasattr(scan_date,"strftime") else str(scan_date)
    badge_style=ParagraphStyle("CB2",fontSize=12,leading=16,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
    badge=Table([[Paragraph(f"{risk_label.upper()} RISK",badge_style)]],colWidths=[55*mm])
    badge.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),risk_color),("TOPPADDING",(0,0),(-1,-1),7),
                               ("BOTTOMPADDING",(0,0),(-1,-1),7),("LEFTPADDING",(0,0),(-1,-1),12),
                               ("RIGHTPADDING",(0,0),(-1,-1),12),("BOX",(0,0),(-1,-1),0.25,risk_color)]))
    meta_rows=[
        ("Target File / Repo",_safe(getattr(scan,"file_name","Unknown"))),
        ("Scan ID",f"#{scan.id}"),
        ("Scan Date",date_str),
        ("Scan Type","Static Application Security Testing"),
        ("Risk Level",risk_label),
        ("Total Findings",f"{s.total}  ·  Critical {s.critical} / High {s.high} / Medium {s.medium} / Low {s.low}"),
    ]
    logo_flow=[]
    if logo_path and os.path.exists(logo_path):
        try:
            logo=Image(logo_path,width=40*mm,height=40*mm)
            logo.hAlign="CENTER"
            logo_flow=[logo,_sp(6)]
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Cover logo render failed: %s", exc)
    return [
        _sp(18),
        *logo_flow,
        Paragraph("DristiScan",st["DS_Cover_Brand"]),
        Paragraph("Intelligent DevSecOps Security Platform",st["DS_Cover_Tag"]),
        _sp(12),
        Paragraph("Security Analysis Report",st["DS_Cover_Title"]),
        Paragraph(_safe(scan.file_name or "Unknown Target"),st["DS_Cover_Sub"]),
        _sp(10),
        Table([[badge]],colWidths=[CONTENT_W],style=[("ALIGN",(0,0),(-1,-1),"CENTER")]),
        _sp(14),
        _info_table(meta_rows),
        _sp(10),
        _rule(C_RULE),
        PageBreak(),
    ]

def _toc(sections):
    st=_styles(); story=[*_section_header("Table of Contents"),_sp(4)]
    for num,title in sections:
        row=Table([[Paragraph(num,st["DS_BodySmall"]),Paragraph(title,st["DS_TOC_Entry"])]],
                  colWidths=[12*mm,CONTENT_W-12*mm])
        row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),3),
                                  ("BOTTOMPADDING",(0,0),(-1,-1),3),("LINEBELOW",(0,0),(-1,-1),0.25,C_RULE)]))
        story.append(row)
    story.append(PageBreak()); return story

def _executive_summary(scan,structured):
    st=_styles(); s=structured.summary; rs=structured.risk_score
    sec_score=max(0.0,100.0-(rs.score*10))
    scan_date=getattr(scan,"scan_date",datetime.utcnow())
    date_str=scan_date.strftime("%Y-%m-%d %H:%M UTC") if hasattr(scan_date,"strftime") else str(scan_date)
    story=[*_section_header("Executive Summary","01")]
    story.append(_sev_count_table(s.critical,s.high,s.medium,s.low)); story.append(_sp(10))
    story.append(_info_table([("TOTAL FINDINGS",str(s.total)),("OVERALL RISK",s.overall_risk),
                               ("RISK SCORE",f"{rs.score:.1f} / 10"),("SECURITY SCORE",f"{sec_score:.0f} / 100"),
                               ("SCAN DATE",date_str),("TARGET",scan.file_name or "Unknown")]))
    story.append(_sp(6))
    if rs.reason: story.append(Paragraph(f"<b>Risk Rationale:</b> {_safe(rs.reason)}",st["DS_Body"]))
    story.append(PageBreak()); return story

def _scan_scope(scan):
    st=_styles(); story=[*_section_header("Scan Scope","02")]
    story.append(_info_table([("TARGET FILE / REPO",scan.file_name or "Unknown"),
                               ("SCAN ENGINE","DristiScan v2 — Rule Engine + AI Agents"),
                               ("SCAN TYPE","Static Application Security Testing (SAST)"),
                               ("SCAN DATE",str(getattr(scan,"scan_date","N/A"))),
                               ("TOTAL ISSUES",str(getattr(scan,"total_findings",0)))]))
    story.append(_sp(4))
    story.append(Paragraph("This report covers static analysis of the submitted source code. Dynamic testing and runtime analysis are outside scope.",st["DS_Body"]))
    story.append(PageBreak()); return story



def _risk_overview(structured):
    st=_styles(); s=structured.summary; story=[*_section_header("Risk Overview","03")]
    cat_counts=Counter(f.type for f in structured.findings)
    if cat_counts:
        hs=ParagraphStyle("RH",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
        cs=ParagraphStyle("RC",fontSize=8,leading=11,textColor=C_TEXT,fontName="Helvetica")
        total=max(s.total,1)
        rows=[[Paragraph("Vulnerability Type",hs),Paragraph("Count",hs),Paragraph("% of Total",hs)]]
        for vtype,cnt in cat_counts.most_common():
            rows.append([Paragraph(_safe(vtype),cs),Paragraph(str(cnt),cs),Paragraph(f"{cnt/total*100:.0f}%",cs)])
        t=Table(rows,colWidths=[CONTENT_W*0.6,CONTENT_W*0.2,CONTENT_W*0.2])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),C_NAVY),("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE,C_OFFWHITE]),
                                ("GRID",(0,0),(-1,-1),0.25,C_RULE),("TOPPADDING",(0,0),(-1,-1),5),
                                ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),8),
                                ("RIGHTPADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(t)
    story.append(PageBreak()); return story

def _ai_insights_section(structured):
    st=_styles(); ins=structured.ai_insights; story=[*_section_header("AI Insights","04")]
    hs=ParagraphStyle("AIH",fontSize=9,leading=13,textColor=C_TEXT,fontName="Helvetica",leftIndent=8,rightIndent=8)
    for label,value in [("Analysis Summary",ins.summary),("Most Critical Issue",ins.most_critical_issue),
                         ("Recommended Fix Priority",ins.fix_priority)]:
        if not value: continue
        story.append(Paragraph(label.upper(),st["DS_Label"]))
        cell=Table([[Paragraph(_safe(value),hs)]],colWidths=[CONTENT_W])
        cell.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0f9ff")),
                                   ("BOX",(0,0),(-1,-1),0.5,C_SLATE_LT),("TOPPADDING",(0,0),(-1,-1),7),
                                   ("BOTTOMPADDING",(0,0),(-1,-1),7),("LEFTPADDING",(0,0),(-1,-1),10),
                                   ("RIGHTPADDING",(0,0),(-1,-1),10)]))
        story.extend([cell,_sp(8)])
    story.append(PageBreak()); return story

def _detailed_findings(structured):
    st=_styles(); findings=structured.findings; story=[*_section_header("Detailed Findings","05")]
    if not findings:
        story.append(Paragraph("No vulnerabilities detected.",st["DS_Body"])); story.append(PageBreak()); return story
    seen=set(); deduped=[]
    for f in findings:
        key=(f.type,f.line)
        if key not in seen: seen.add(key); deduped.append(f)
    for idx,finding in enumerate(deduped,1):
        sev=finding.severity; sc=SEV_COLORS.get(sev,C_SLATE)
        ns=ParagraphStyle("FN",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold")
        ts=ParagraphStyle("FT",fontSize=10,leading=13,textColor=C_WHITE,fontName="Helvetica-Bold")
        ss=ParagraphStyle("FS",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_RIGHT)
        hr=Table([[Paragraph(f"{idx:02d}",ns),Paragraph(_safe(finding.type),ts),Paragraph(sev.upper(),ss)]],
                 colWidths=[10*mm,CONTENT_W-30*mm,20*mm])
        hr.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),sc),("TOPPADDING",(0,0),(-1,-1),6),
                                  ("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8),
                                  ("RIGHTPADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(hr)
        if finding.line: story.append(Paragraph(f"Line {finding.line}",st["DS_BodySmall"]))
        story.append(_sp(4))
        for label,value in [("DESCRIPTION",finding.description),("IMPACT",finding.impact),
                              ("ATTACK EXAMPLE",finding.attack_example),("RECOMMENDATION",finding.recommendation)]:
            if value and value.strip():
                story.append(Paragraph(label,st["DS_Label"])); story.append(Paragraph(_safe(value),st["DS_Body"])); story.append(_sp(3))
        if finding.code and finding.code.strip():
            story.append(Paragraph("AFFECTED CODE",st["DS_Label"])); story.append(_code_block(finding.code)); story.append(_sp(3))
        if finding.fix_code and finding.fix_code.strip():
            story.append(Paragraph("SECURE CODE EXAMPLE",st["DS_Label"])); story.append(_code_block(finding.fix_code)); story.append(_sp(3))
        story.append(_rule(C_RULE)); story.append(_sp(6))
    story.append(PageBreak()); return story



def _secret_section(structured):
    st=_styles()
    secrets=[f for f in structured.findings if any(k in f.type.lower() for k in ("secret","key","credential","token","password"))]
    if not secrets: return []
    story=[*_section_header("Secret Exposure","06")]
    story.append(Paragraph(f"{len(secrets)} hardcoded secret(s) detected. Rotate all exposed credentials immediately.",st["DS_Body"]))
    story.append(_sp(6))
    for sf in secrets:
        story.append(Paragraph(f"▸  {_safe(sf.type)}",st["DS_H2"]))
        story.append(_info_table([("SEVERITY",sf.severity),("LINE",str(sf.line) if sf.line else "N/A"),
                                   ("RECOMMENDATION",sf.recommendation or "Rotate and move to secrets manager.")]))
        story.append(_sp(6))
    story.append(PageBreak()); return story

def _dependency_section(structured):
    st=_styles()
    deps=[f for f in structured.findings if any(k in f.type.lower() for k in ("depend","package","library","cve"))]
    if not deps: return []
    story=[*_section_header("Dependency Vulnerabilities","07")]
    hs=ParagraphStyle("DH",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
    cs=ParagraphStyle("DC",fontSize=8,leading=11,textColor=C_TEXT,fontName="Helvetica")
    rows=[[Paragraph(h,hs) for h in ["Package / Type","Severity","Description","Fix"]]]
    cw=[CONTENT_W*0.25,CONTENT_W*0.12,CONTENT_W*0.38,CONTENT_W*0.25]
    for dep in deps:
        rows.append([Paragraph(_safe(dep.type),cs),Paragraph(_safe(dep.severity),cs),
                     Paragraph(_safe(dep.description[:120]),cs),Paragraph(_safe(dep.recommendation[:80]),cs)])
    t=Table(rows,colWidths=cw)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),C_NAVY),("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE,C_OFFWHITE]),
                            ("GRID",(0,0),(-1,-1),0.25,C_RULE),("TOPPADDING",(0,0),(-1,-1),5),
                            ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),
                            ("RIGHTPADDING",(0,0),(-1,-1),6),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(t); story.append(PageBreak()); return story

def _risk_prioritization(structured):
    st=_styles(); story=[*_section_header("Risk Prioritization","08")]
    story.append(Paragraph("Address findings in the following order based on severity:",st["DS_Body"])); story.append(_sp(6))
    ordered=sorted(structured.findings,key=lambda f:["Critical","High","Medium","Low"].index(f.severity) if f.severity in ["Critical","High","Medium","Low"] else 99)
    for rank,finding in enumerate(ordered[:15],1):
        sc=SEV_COLORS.get(finding.severity,C_SLATE)
        rs2=ParagraphStyle("RP",fontSize=9,leading=11,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
        rt=ParagraphStyle("RT",fontSize=9,leading=12,textColor=C_TEXT,fontName="Helvetica-Bold")
        rv=ParagraphStyle("RV",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER)
        row=Table([[Paragraph(str(rank),rs2),Paragraph(_safe(finding.type),rt),Paragraph(finding.severity,rv)]],
                  colWidths=[10*mm,CONTENT_W-30*mm,20*mm])
        row.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),C_NAVY),("BACKGROUND",(2,0),(2,-1),sc),
                                   ("BACKGROUND",(1,0),(1,-1),C_OFFWHITE),("TOPPADDING",(0,0),(-1,-1),5),
                                   ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),
                                   ("RIGHTPADDING",(0,0),(-1,-1),6),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                   ("LINEBELOW",(0,0),(-1,-1),0.25,C_RULE)]))
        story.append(row)
    story.append(PageBreak()); return story

def _recommendations_section(structured):
    st=_styles(); story=[*_section_header("Recommendations","09")]
    recs=list({f.recommendation for f in structured.findings if f.recommendation})
    if not recs: story.append(Paragraph("No specific recommendations available.",st["DS_Body"]))
    for i,rec in enumerate(recs[:20],1):
        story.append(Paragraph(f"{i}.  {_safe(rec)}",st["DS_Body"])); story.append(_sp(3))
    story.append(PageBreak()); return story

def _compliance_section(structured):
    st=_styles(); story=[*_section_header("Compliance & References","10")]
    owasp_map={"SQL Injection":"A03:2021 – Injection","Command Injection":"A03:2021 – Injection",
               "XSS":"A03:2021 – Injection","Hardcoded":"A02:2021 – Cryptographic Failures",
               "Secret":"A02:2021 – Cryptographic Failures","Path Traversal":"A01:2021 – Broken Access Control",
               "Dependency":"A06:2021 – Vulnerable Components"}
    hs=ParagraphStyle("CH",fontSize=8,leading=10,textColor=C_WHITE,fontName="Helvetica-Bold")
    cs=ParagraphStyle("CC",fontSize=8,leading=11,textColor=C_TEXT,fontName="Helvetica")
    rows=[[Paragraph(h,hs) for h in ["Finding Type","OWASP Top 10","CWE Reference"]]]
    cw=[CONTENT_W*0.35,CONTENT_W*0.40,CONTENT_W*0.25]; seen_types=set()
    for f in structured.findings:
        if f.type in seen_types: continue
        seen_types.add(f.type)
        owasp=next((v for k,v in owasp_map.items() if k.lower() in f.type.lower()),"—")
        rows.append([Paragraph(_safe(f.type),cs),Paragraph(owasp,cs),Paragraph("—",cs)])
    t=Table(rows,colWidths=cw)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),C_NAVY),("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE,C_OFFWHITE]),
                            ("GRID",(0,0),(-1,-1),0.25,C_RULE),("TOPPADDING",(0,0),(-1,-1),5),
                            ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),8),
                            ("RIGHTPADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(t); story.append(_sp(8))
    story.append(Paragraph("References: OWASP Top 10 (2021) · NIST NVD · MITRE CWE · CVE Database",st["DS_BodySmall"]))
    return story



# ── public API — unchanged signatures ────────────────────────────────────────

def _get_scan_or_404(db: Session, scan_id: int, user_id: int | None = None) -> Scan:
    query = db.query(Scan).filter(Scan.id == scan_id)
    if user_id is not None:
        query = query.filter(Scan.user_id == user_id)
    scan = query.first()
    if not scan:
        detail = "Not authorized to access this report" if user_id is not None else "Scan not found"
        code = status.HTTP_403_FORBIDDEN if user_id is not None else status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=detail)
    return scan


def get_report(db: Session, scan_id: int, user_id: int | None = None) -> Report:
    scan = _get_scan_or_404(db, scan_id, user_id=user_id)
    return Report(
        scan_id=scan.id, file_name=scan.file_name, display_file_name=scan.file_name,
        scan_date=scan.scan_date, total_vulnerabilities=getattr(scan,"total_findings",0),
        risk_score=getattr(scan,"risk_score",0.0), security_score=getattr(scan,"security_score",0.0),
        critical_count=getattr(scan,"critical_count",0), high_count=getattr(scan,"high_count",0),
        medium_count=getattr(scan,"medium_count",0), low_count=getattr(scan,"low_count",0),
        risk_level=risk_level(scan.risk_score), vulnerabilities=list(scan.vulnerabilities),
    )


def get_structured_report(db: Session, scan_id: int, user_id: int | None = None) -> FullStructuredReportSchema:
    scan = _get_scan_or_404(db, scan_id, user_id=user_id)
    return build_structured_report(scan)


def get_report_pdf(db: Session, scan_id: int, user_id: int | None = None) -> bytes:
    scan = _get_scan_or_404(db, scan_id, user_id=user_id)
    structured = build_structured_report(scan)
    buffer = BytesIO()
    doc = _DSDocTemplate(
        buffer,
        scan_id=str(scan.id),
        file_name=scan.file_name or "",
        logo_path=settings.report_logo_path,
        pagesize=A4,
        leftMargin=ML,
        rightMargin=MR,
        topMargin=MT,
        bottomMargin=MB,
    )
    toc_entries = [
        ("01","Executive Summary"),("02","Scan Scope"),("03","Risk Overview"),
        ("04","AI Insights"),("05","Detailed Findings"),("06","Secret Exposure"),
        ("07","Dependency Vulnerabilities"),("08","Risk Prioritization"),
        ("09","Recommendations"),("10","Compliance & References"),
    ]
    story: List = [
        NextPageTemplate("Cover"), *_cover_page(scan, structured, settings.report_logo_path),
        NextPageTemplate("Inner"), *_toc(toc_entries),
        *_executive_summary(scan, structured), *_scan_scope(scan),
        *_risk_overview(structured), *_ai_insights_section(structured),
        *_detailed_findings(structured), *_secret_section(structured),
        *_dependency_section(structured), *_risk_prioritization(structured),
        *_recommendations_section(structured), *_compliance_section(structured),
    ]
    doc.build(story)
    return buffer.getvalue()
