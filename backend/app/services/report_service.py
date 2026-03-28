"""DristiScan PDF Report Generator — clean professional audit layout."""
from __future__ import annotations
import logging, os
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
    BaseDocTemplate, Frame, HRFlowable, Image, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from sqlalchemy.orm import Session
from ..models.scan_model import Scan
from ..schemas.report_schema import FullStructuredReportSchema, Report
from .risk_engine import risk_level
from .structured_report import build_structured_report

logger = logging.getLogger("dristi-scan")

# ── page geometry ─────────────────────────────────────────────────────────────
PW, PH = A4
ML, MR = 22*mm, 22*mm
MT, MB = 28*mm, 22*mm
CW = PW - ML - MR          # content width

# ── clean color palette (NO dark backgrounds) ─────────────────────────────────
C_BLACK   = colors.HexColor("#111827")   # headings
C_DARK    = colors.HexColor("#374151")   # body text
C_GRAY    = colors.HexColor("#6B7280")   # secondary text
C_LGRAY   = colors.HexColor("#D1D5DB")   # borders / rules
C_XLGRAY  = colors.HexColor("#F9FAFB")   # alternating row tint
C_WHITE   = colors.white
C_BLUE    = colors.HexColor("#1D4ED8")   # accent headings
C_BLUE_LT = colors.HexColor("#EFF6FF")   # very light blue tint (AI insights)
C_BLUE_BD = colors.HexColor("#BFDBFE")   # light blue border

# severity — used ONLY for badges / text, never as full backgrounds
SEV = {
    "Critical": colors.HexColor("#DC2626"),
    "High":     colors.HexColor("#EA580C"),
    "Medium":   colors.HexColor("#D97706"),
    "Low":      colors.HexColor("#16A34A"),
}
SEV_BG = {
    "Critical": colors.HexColor("#FEF2F2"),
    "High":     colors.HexColor("#FFF7ED"),
    "Medium":   colors.HexColor("#FFFBEB"),
    "Low":      colors.HexColor("#F0FDF4"),
}

LOGO_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "docs", "screens", "logo.png"
)
THEME_BG = C_WHITE   # kept for legacy callers

# ── style registry ────────────────────────────────────────────────────────────
_SC = None
def _S():
    global _SC
    if _SC: return _SC
    b = getSampleStyleSheet()
    def a(n, **kw):
        if n not in b: b.add(ParagraphStyle(name=n, **kw))
    a("Cover_Title",  fontSize=26, leading=32, textColor=C_BLACK,  fontName="Helvetica-Bold",  alignment=TA_CENTER, spaceAfter=8)
    a("Cover_Tag",    fontSize=12, leading=16, textColor=C_BLUE,   fontName="Helvetica",       alignment=TA_CENTER, spaceAfter=6)
    a("Cover_Sub",    fontSize=10, leading=14, textColor=C_GRAY,   fontName="Helvetica",       alignment=TA_CENTER, spaceAfter=4)
    a("Sec_Title",    fontSize=14, leading=18, textColor=C_BLUE,   fontName="Helvetica-Bold",  spaceBefore=14, spaceAfter=4)
    a("Sub_Title",    fontSize=11, leading=14, textColor=C_BLACK,  fontName="Helvetica-Bold",  spaceBefore=8,  spaceAfter=3)
    a("Body",         fontSize=9,  leading=13, textColor=C_DARK,   fontName="Helvetica",       spaceAfter=4)
    a("Body_Small",   fontSize=8,  leading=12, textColor=C_GRAY,   fontName="Helvetica",       spaceAfter=2)
    a("Code",         fontSize=8,  leading=12, textColor=C_BLACK,  fontName="Courier",         spaceAfter=4, leftIndent=4)
    a("Label",        fontSize=7,  leading=10, textColor=C_GRAY,   fontName="Helvetica-Bold",  spaceAfter=1, spaceBefore=4)
    a("TOC_Entry",    fontSize=9,  leading=14, textColor=C_DARK,   fontName="Helvetica",       spaceAfter=2)
    _SC = b; return b

# ── reusable helpers ──────────────────────────────────────────────────────────
def _sp(h=6):  return Spacer(1, h)
def _safe(t):  return escape(str(t or ""))
def _rule(w="100%", color=None, thick=0.5):
    return HRFlowable(width=w, thickness=thick, color=color or C_LGRAY, spaceAfter=6, spaceBefore=2)

def section_title(text):
    """Bold blue section heading + thin rule."""
    return [Paragraph(text, _S()["Sec_Title"]), _rule(thick=0.75, color=C_BLUE)]

def code_block(code):
    """Light-gray monospace code block — no dark theme."""
    if not code or not str(code).strip():
        return Paragraph("N/A", _S()["Body_Small"])
    lines = str(code).strip().splitlines()[:50]
    cell = Paragraph(_safe("\n".join(lines)), _S()["Code"])
    t = Table([[cell]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#F5F5F5")),
        ("BOX",           (0,0),(-1,-1), 0.5, C_LGRAY),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    return t

def info_row(label, value):
    """Single label/value row — no background."""
    st = _S()
    t = Table(
        [[Paragraph(_safe(label), st["Label"]), Paragraph(_safe(value), st["Body"])]],
        colWidths=[50*mm, CW - 50*mm],
    )
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("LINEBELOW",     (0,0),(-1,-1), 0.25, C_LGRAY),
    ]))
    return t

def sev_badge(sev):
    """Inline severity badge — colored text on very light tint, thin border."""
    color  = SEV.get(sev, C_GRAY)
    bg     = SEV_BG.get(sev, C_WHITE)
    style  = ParagraphStyle("SB", fontSize=7, leading=9, textColor=color,
                             fontName="Helvetica-Bold", alignment=TA_CENTER)
    t = Table([[Paragraph(sev.upper(), style)]], colWidths=[20*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("BOX",           (0,0),(-1,-1), 0.5, color),
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    return t

def table_style():
    """Clean table: white bg, light alternating rows, thin grid."""
    return TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  colors.HexColor("#F3F4F6")),
        ("TEXTCOLOR",     (0,0),(-1,0),  C_BLACK),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_XLGRAY]),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.25, C_LGRAY),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ])

# ── page template (header + footer on inner pages) ────────────────────────────
class _Doc(BaseDocTemplate):
    def __init__(self, buf, scan_id, file_name, **kw):
        super().__init__(buf, **kw)
        self._sid = scan_id; self._fn = file_name
        cover_f = Frame(ML, MB, CW, PH - MT - MB, id="cover")
        inner_f = Frame(ML, MB + 12*mm, CW, PH - MT - MB - 12*mm, id="inner")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_f], onPage=self._cover_bg),
            PageTemplate(id="Inner", frames=[inner_f], onPage=self._inner_chrome),
        ])

    def _cover_bg(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
        # thin blue accent bar at very bottom
        canvas.setFillColor(C_BLUE)
        canvas.rect(0, 0, PW, 3*mm, fill=1, stroke=0)
        canvas.restoreState()

    def _inner_chrome(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
        # header: logo text + thin rule
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(C_BLUE)
        canvas.drawString(ML, PH - 14*mm, "DristiScan")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(ML + 26*mm, PH - 14*mm, "Security Analysis Report")
        fn = (self._fn or "")[:55]
        canvas.drawRightString(PW - MR, PH - 14*mm, fn)
        canvas.setStrokeColor(C_LGRAY)
        canvas.setLineWidth(0.5)
        canvas.line(ML, PH - 16*mm, PW - MR, PH - 16*mm)
        # footer rule + text
        canvas.line(ML, MB + 8*mm, PW - MR, MB + 8*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(ML, MB + 4*mm, f"Confidential \u2013 DristiScan  \u00b7  Scan #{self._sid}")
        canvas.drawRightString(PW - MR, MB + 4*mm, f"Page {doc.page}")
        canvas.restoreState()


# ── section builders ──────────────────────────────────────────────────────────

def _cover(scan, structured):
    st = _S(); s = structured.summary
    risk_label = s.overall_risk
    risk_color = SEV.get(risk_label, C_GRAY)
    risk_bg    = SEV_BG.get(risk_label, C_WHITE)
    scan_date  = getattr(scan, "scan_date", datetime.utcnow())
    date_str   = scan_date.strftime("%B %d, %Y") if hasattr(scan_date, "strftime") else str(scan_date)

    story = [_sp(20)]
    # logo
    logo = os.path.abspath(LOGO_PATH)
    if os.path.exists(logo):
        img = Image(logo, width=40*mm, height=40*mm)
        story.append(Table([[img]], colWidths=[CW], style=[("ALIGN",(0,0),(-1,-1),"CENTER")]))
        story.append(_sp(10))
    # title block
    story += [
        Paragraph("Security Analysis Report", st["Cover_Title"]),
        Paragraph("Intelligent DevSecOps Security Platform", st["Cover_Tag"]),
        _sp(6),
        _rule(thick=1, color=C_BLUE),
        _sp(10),
        Paragraph(_safe(scan.file_name or "Unknown Target"), ParagraphStyle(
            "CFile", fontSize=13, leading=17, textColor=C_BLACK,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)),
    ]
    # meta pills
    meta_s = ParagraphStyle("CMeta", fontSize=9, leading=13, textColor=C_GRAY,
                             fontName="Helvetica", alignment=TA_CENTER, spaceAfter=3)
    story += [
        Paragraph(f"Scan ID: #{scan.id}", meta_s),
        Paragraph(f"Date: {date_str}", meta_s),
        _sp(14),
    ]
    # risk badge — light tint, colored border
    badge_s = ParagraphStyle("CBadge", fontSize=12, leading=16, textColor=risk_color,
                              fontName="Helvetica-Bold", alignment=TA_CENTER)
    badge_t = Table([[Paragraph(f"{risk_label.upper()} RISK", badge_s)]], colWidths=[50*mm])
    badge_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), risk_bg),
        ("BOX",           (0,0),(-1,-1), 1.5, risk_color),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
    ]))
    story.append(Table([[badge_t]], colWidths=[CW], style=[("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(_sp(16))
    # summary counts
    counts_s = ParagraphStyle("CCnt", fontSize=9, leading=13, textColor=C_GRAY,
                               fontName="Helvetica", alignment=TA_CENTER)
    story.append(Paragraph(
        f"Total Findings: {s.total}  \u00b7  Critical: {s.critical}  \u00b7  "
        f"High: {s.high}  \u00b7  Medium: {s.medium}  \u00b7  Low: {s.low}", counts_s))
    story.append(PageBreak())
    return story


def _toc(sections):
    st = _S()
    story = [*section_title("Table of Contents"), _sp(6)]
    for num, title in sections:
        row = Table(
            [[Paragraph(num, st["Body_Small"]), Paragraph(title, st["TOC_Entry"])]],
            colWidths=[12*mm, CW - 12*mm],
        )
        row.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("TOPPADDING",    (0,0),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
            ("LINEBELOW",     (0,0),(-1,-1), 0.25, C_LGRAY),
        ]))
        story.append(row)
    story.append(PageBreak())
    return story


def _exec_summary(scan, structured):
    st = _S(); s = structured.summary; rs = structured.risk_score
    sec_score = max(0.0, 100.0 - rs.score * 10)
    scan_date = getattr(scan, "scan_date", datetime.utcnow())
    date_str  = scan_date.strftime("%Y-%m-%d %H:%M UTC") if hasattr(scan_date, "strftime") else str(scan_date)

    story = [*section_title("01  Executive Summary"), _sp(8)]

    # 4-column severity summary — light tint, colored text, thin border
    cw4 = CW / 4
    hs = ParagraphStyle("ESH", fontSize=8, leading=10, textColor=C_GRAY,
                         fontName="Helvetica-Bold", alignment=TA_CENTER)
    vs = ParagraphStyle("ESV", fontSize=22, leading=26, fontName="Helvetica-Bold", alignment=TA_CENTER)
    data = [
        [Paragraph("CRITICAL", hs), Paragraph("HIGH", hs), Paragraph("MEDIUM", hs), Paragraph("LOW", hs)],
        [Paragraph(str(s.critical), ParagraphStyle("ESC", parent=vs, textColor=SEV["Critical"])),
         Paragraph(str(s.high),     ParagraphStyle("ESH2",parent=vs, textColor=SEV["High"])),
         Paragraph(str(s.medium),   ParagraphStyle("ESM", parent=vs, textColor=SEV["Medium"])),
         Paragraph(str(s.low),      ParagraphStyle("ESL", parent=vs, textColor=SEV["Low"]))],
    ]
    sev_t = Table(data, colWidths=[cw4]*4)
    sev_t.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.5, C_LGRAY),
        ("LINEAFTER",     (0,0),(2,-1),  0.25, C_LGRAY),
        ("LINEBELOW",     (0,0),(-1,0),  0.25, C_LGRAY),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(sev_t); story.append(_sp(10))

    # key metrics
    for label, value in [
        ("Total Findings",  str(s.total)),
        ("Overall Risk",    s.overall_risk),
        ("Risk Score",      f"{rs.score:.1f} / 10"),
        ("Security Score",  f"{sec_score:.0f} / 100"),
        ("Scan Date",       date_str),
        ("Target",          scan.file_name or "Unknown"),
    ]:
        story.append(info_row(label, value))
    story.append(_sp(6))
    if rs.reason:
        story.append(Paragraph(f"<b>Risk Rationale:</b> {_safe(rs.reason)}", st["Body"]))
    story.append(PageBreak())
    return story


def _scan_scope(scan):
    st = _S()
    story = [*section_title("02  Scan Scope"), _sp(6)]
    for label, value in [
        ("Target File / Repo", scan.file_name or "Unknown"),
        ("Scan Engine",        "DristiScan v2 \u2014 Rule Engine + AI Agents"),
        ("Scan Type",          "Static Application Security Testing (SAST)"),
        ("Scan Date",          str(getattr(scan, "scan_date", "N/A"))),
        ("Total Issues",       str(getattr(scan, "total_findings", 0))),
    ]:
        story.append(info_row(label, value))
    story.append(_sp(4))
    story.append(Paragraph(
        "This report covers static analysis of the submitted source code. "
        "Dynamic testing, penetration testing, and runtime analysis are outside scope.",
        st["Body"]))
    story.append(PageBreak())
    return story

# ── page template (header + footer on inner pages) ────────────────────────────
class _Doc(BaseDocTemplate):
    def __init__(self, buf, scan_id, file_name, **kw):
        super().__init__(buf, **kw)
        self._sid = scan_id; self._fn = file_name
        cover_f = Frame(ML, MB, CW, PH - MT - MB, id="cover")
        inner_f = Frame(ML, MB + 12*mm, CW, PH - MT - MB - 12*mm, id="inner")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_f], onPage=self._cover_bg),
            PageTemplate(id="Inner", frames=[inner_f], onPage=self._inner_chrome),
        ])

    def _cover_bg(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
        # thin blue accent bar at very bottom
        canvas.setFillColor(C_BLUE)
        canvas.rect(0, 0, PW, 3*mm, fill=1, stroke=0)
        canvas.restoreState()

    def _inner_chrome(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
        # header: logo text + thin rule
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(C_BLUE)
        canvas.drawString(ML, PH - 14*mm, "DristiScan")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(ML + 26*mm, PH - 14*mm, "Security Analysis Report")
        fn = (self._fn or "")[:55]
        canvas.drawRightString(PW - MR, PH - 14*mm, fn)
        canvas.setStrokeColor(C_LGRAY)
        canvas.setLineWidth(0.5)
        canvas.line(ML, PH - 16*mm, PW - MR, PH - 16*mm)
        # footer rule + text
        canvas.line(ML, MB + 8*mm, PW - MR, MB + 8*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(ML, MB + 4*mm, f"Confidential \u2013 DristiScan  \u00b7  Scan #{self._sid}")
        canvas.drawRightString(PW - MR, MB + 4*mm, f"Page {doc.page}")
        canvas.restoreState()


# ── section builders ──────────────────────────────────────────────────────────

def _cover(scan, structured):
    st = _S(); s = structured.summary
    risk_label = s.overall_risk
    risk_color = SEV.get(risk_label, C_GRAY)
    risk_bg    = SEV_BG.get(risk_label, C_WHITE)
    scan_date  = getattr(scan, "scan_date", datetime.utcnow())
    date_str   = scan_date.strftime("%B %d, %Y") if hasattr(scan_date, "strftime") else str(scan_date)

    story = [_sp(20)]
    # logo
    logo = os.path.abspath(LOGO_PATH)
    if os.path.exists(logo):
        img = Image(logo, width=40*mm, height=40*mm)
        story.append(Table([[img]], colWidths=[CW], style=[("ALIGN",(0,0),(-1,-1),"CENTER")]))
        story.append(_sp(10))
    # title block
    story += [
        Paragraph("Security Analysis Report", st["Cover_Title"]),
        Paragraph("Intelligent DevSecOps Security Platform", st["Cover_Tag"]),
        _sp(6),
        _rule(thick=1, color=C_BLUE),
        _sp(10),
        Paragraph(_safe(scan.file_name or "Unknown Target"), ParagraphStyle(
            "CFile", fontSize=13, leading=17, textColor=C_BLACK,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)),
    ]
    # meta pills
    meta_s = ParagraphStyle("CMeta", fontSize=9, leading=13, textColor=C_GRAY,
                             fontName="Helvetica", alignment=TA_CENTER, spaceAfter=3)
    story += [
        Paragraph(f"Scan ID: #{scan.id}", meta_s),
        Paragraph(f"Date: {date_str}", meta_s),
        _sp(14),
    ]
    # risk badge — light tint, colored border
    badge_s = ParagraphStyle("CBadge", fontSize=12, leading=16, textColor=risk_color,
                              fontName="Helvetica-Bold", alignment=TA_CENTER)
    badge_t = Table([[Paragraph(f"{risk_label.upper()} RISK", badge_s)]], colWidths=[50*mm])
    badge_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), risk_bg),
        ("BOX",           (0,0),(-1,-1), 1.5, risk_color),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
    ]))
    story.append(Table([[badge_t]], colWidths=[CW], style=[("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(_sp(16))
    # summary counts
    counts_s = ParagraphStyle("CCnt", fontSize=9, leading=13, textColor=C_GRAY,
                               fontName="Helvetica", alignment=TA_CENTER)
    story.append(Paragraph(
        f"Total Findings: {s.total}  \u00b7  Critical: {s.critical}  \u00b7  "
        f"High: {s.high}  \u00b7  Medium: {s.medium}  \u00b7  Low: {s.low}", counts_s))
    story.append(PageBreak())
    return story


def _toc(sections):
    st = _S()
    story = [*section_title("Table of Contents"), _sp(6)]
    for num, title in sections:
        row = Table(
            [[Paragraph(num, st["Body_Small"]), Paragraph(title, st["TOC_Entry"])]],
            colWidths=[12*mm, CW - 12*mm],
        )
        row.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("TOPPADDING",    (0,0),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
            ("LINEBELOW",     (0,0),(-1,-1), 0.25, C_LGRAY),
        ]))
        story.append(row)
    story.append(PageBreak())
    return story


def _exec_summary(scan, structured):
    st = _S(); s = structured.summary; rs = structured.risk_score
    sec_score = max(0.0, 100.0 - rs.score * 10)
    scan_date = getattr(scan, "scan_date", datetime.utcnow())
    date_str  = scan_date.strftime("%Y-%m-%d %H:%M UTC") if hasattr(scan_date, "strftime") else str(scan_date)

    story = [*section_title("01  Executive Summary"), _sp(8)]

    # 4-column severity summary — light tint, colored text, thin border
    cw4 = CW / 4
    hs = ParagraphStyle("ESH", fontSize=8, leading=10, textColor=C_GRAY,
                         fontName="Helvetica-Bold", alignment=TA_CENTER)
    vs = ParagraphStyle("ESV", fontSize=22, leading=26, fontName="Helvetica-Bold", alignment=TA_CENTER)
    data = [
        [Paragraph("CRITICAL", hs), Paragraph("HIGH", hs), Paragraph("MEDIUM", hs), Paragraph("LOW", hs)],
        [Paragraph(str(s.critical), ParagraphStyle("ESC", parent=vs, textColor=SEV["Critical"])),
         Paragraph(str(s.high),     ParagraphStyle("ESH2",parent=vs, textColor=SEV["High"])),
         Paragraph(str(s.medium),   ParagraphStyle("ESM", parent=vs, textColor=SEV["Medium"])),
         Paragraph(str(s.low),      ParagraphStyle("ESL", parent=vs, textColor=SEV["Low"]))],
    ]
    sev_t = Table(data, colWidths=[cw4]*4)
    sev_t.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.5, C_LGRAY),
        ("LINEAFTER",     (0,0),(2,-1),  0.25, C_LGRAY),
        ("LINEBELOW",     (0,0),(-1,0),  0.25, C_LGRAY),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(sev_t); story.append(_sp(10))

    # key metrics
    for label, value in [
        ("Total Findings",  str(s.total)),
        ("Overall Risk",    s.overall_risk),
        ("Risk Score",      f"{rs.score:.1f} / 10"),
        ("Security Score",  f"{sec_score:.0f} / 100"),
        ("Scan Date",       date_str),
        ("Target",          scan.file_name or "Unknown"),
    ]:
        story.append(info_row(label, value))
    story.append(_sp(6))
    if rs.reason:
        story.append(Paragraph(f"<b>Risk Rationale:</b> {_safe(rs.reason)}", st["Body"]))
    story.append(PageBreak())
    return story


def _scan_scope(scan):
    st = _S()
    story = [*section_title("02  Scan Scope"), _sp(6)]
    for label, value in [
        ("Target File / Repo", scan.file_name or "Unknown"),
        ("Scan Engine",        "DristiScan v2 \u2014 Rule Engine + AI Agents"),
        ("Scan Type",          "Static Application Security Testing (SAST)"),
        ("Scan Date",          str(getattr(scan, "scan_date", "N/A"))),
        ("Total Issues",       str(getattr(scan, "total_findings", 0))),
    ]:
        story.append(info_row(label, value))
    story.append(_sp(4))
    story.append(Paragraph(
        "This report covers static analysis of the submitted source code. "
        "Dynamic testing, penetration testing, and runtime analysis are outside scope.",
        st["Body"]))
    story.append(PageBreak())
    return story

def _risk_overview(structured):
    st = _S(); s = structured.summary
    story = [*section_title("03  Risk Overview"), _sp(6)]
    cat_counts = Counter(f.type for f in structured.findings)
    if cat_counts:
        total = max(s.total, 1)
        hs = ParagraphStyle("ROH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
        cs = ParagraphStyle("ROC", fontSize=8, leading=11, textColor=C_DARK,  fontName="Helvetica")
        rows = [[Paragraph(h, hs) for h in ["Vulnerability Type", "Count", "% of Total"]]]
        for vtype, cnt in cat_counts.most_common():
            rows.append([Paragraph(_safe(vtype), cs), Paragraph(str(cnt), cs),
                         Paragraph(f"{cnt/total*100:.0f}%", cs)])
        t = Table(rows, colWidths=[CW*0.6, CW*0.2, CW*0.2])
        t.setStyle(table_style())
        story.append(t)
    story.append(PageBreak()); return story


def _ai_insights(structured):
    st = _S(); ins = structured.ai_insights
    story = [*section_title("04  AI Insights"), _sp(6)]
    hs = ParagraphStyle("AIH", fontSize=9, leading=13, textColor=C_DARK,
                         fontName="Helvetica", leftIndent=8, rightIndent=8)
    for label, value in [
        ("Analysis Summary",         ins.summary),
        ("Most Critical Issue",      ins.most_critical_issue),
        ("Recommended Fix Priority", ins.fix_priority),
    ]:
        if not value: continue
        story.append(Paragraph(label.upper(), st["Label"]))
        cell = Table([[Paragraph(_safe(value), hs)]], colWidths=[CW])
        cell.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BLUE_LT),
            ("BOX",           (0,0),(-1,-1), 0.75, C_BLUE_BD),
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ]))
        story.extend([cell, _sp(8)])
    story.append(PageBreak()); return story


def _findings(structured):
    st = _S(); findings = structured.findings
    story = [*section_title("05  Detailed Findings"), _sp(6)]
    if not findings:
        story.append(Paragraph("No vulnerabilities detected.", st["Body"]))
        story.append(PageBreak()); return story
    # deduplicate
    seen = set(); deduped = []
    for f in findings:
        k = (f.type, f.line)
        if k not in seen: seen.add(k); deduped.append(f)
    for idx, finding in enumerate(deduped, 1):
        sev = finding.severity
        # finding header: number + name + severity badge (no colored background)
        num_s  = ParagraphStyle(f"FN{idx}", fontSize=9,  leading=11, textColor=C_GRAY,  fontName="Helvetica-Bold")
        type_s = ParagraphStyle(f"FT{idx}", fontSize=11, leading=14, textColor=C_BLACK, fontName="Helvetica-Bold")
        hdr = Table(
            [[Paragraph(f"{idx:02d}", num_s), Paragraph(_safe(finding.type), type_s), sev_badge(sev)]],
            colWidths=[10*mm, CW - 30*mm, 20*mm],
        )
        hdr.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ]))
        story.append(hdr); story.append(_sp(3))
        if finding.line:
            story.append(Paragraph(f"File / Line: {finding.line}", st["Body_Small"]))
        story.append(_rule(thick=0.25))
        story.append(_sp(3))
        for label, value in [
            ("Description",      finding.description),
            ("Impact",           finding.impact),
            ("Attack Example",   finding.attack_example),
            ("Recommendation",   finding.recommendation),
        ]:
            if value and str(value).strip():
                story.append(Paragraph(label.upper(), st["Label"]))
                story.append(Paragraph(_safe(value), st["Body"]))
                story.append(_sp(2))
        if finding.code and str(finding.code).strip():
            story.append(Paragraph("AFFECTED CODE", st["Label"]))
            story.append(code_block(finding.code)); story.append(_sp(3))
        if finding.fix_code and str(finding.fix_code).strip():
            story.append(Paragraph("SECURE CODE EXAMPLE", st["Label"]))
            story.append(code_block(finding.fix_code)); story.append(_sp(3))
        story.append(_rule(thick=0.5, color=C_LGRAY)); story.append(_sp(8))
    story.append(PageBreak()); return story


def _secrets(structured):
    st = _S()
    secs = [f for f in structured.findings
            if any(k in f.type.lower() for k in ("secret","key","credential","token","password"))]
    if not secs: return []
    story = [*section_title("06  Secret Exposure"), _sp(4)]
    story.append(Paragraph(
        f"{len(secs)} hardcoded secret(s) detected. Rotate all exposed credentials immediately.",
        st["Body"]))
    story.append(_sp(6))
    for sf in secs:
        story.append(Paragraph(f"\u25b8  {_safe(sf.type)}", st["Sub_Title"]))
        for label, value in [("Severity", sf.severity), ("Line", str(sf.line) if sf.line else "N/A"),
                              ("Recommendation", sf.recommendation or "Rotate and move to secrets manager.")]:
            story.append(info_row(label, value))
        story.append(_sp(6))
    story.append(PageBreak()); return story


def _deps(structured):
    st = _S()
    deps = [f for f in structured.findings
            if any(k in f.type.lower() for k in ("depend","package","library","cve"))]
    if not deps: return []
    story = [*section_title("07  Dependency Vulnerabilities"), _sp(4)]
    hs = ParagraphStyle("DH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
    cs = ParagraphStyle("DC", fontSize=8, leading=11, textColor=C_DARK,  fontName="Helvetica")
    rows = [[Paragraph(h, hs) for h in ["Package / Type", "Severity", "Description", "Fix"]]]
    cw = [CW*0.25, CW*0.12, CW*0.38, CW*0.25]
    for dep in deps:
        rows.append([Paragraph(_safe(dep.type), cs), Paragraph(_safe(dep.severity), cs),
                     Paragraph(_safe(dep.description[:120]), cs),
                     Paragraph(_safe(dep.recommendation[:80]), cs)])
    t = Table(rows, colWidths=cw); t.setStyle(table_style())
    story.append(t); story.append(PageBreak()); return story


def _prioritization(structured):
    st = _S()
    story = [*section_title("08  Risk Prioritization"), _sp(4)]
    story.append(Paragraph("Address findings in the following order:", st["Body"])); story.append(_sp(6))
    ordered = sorted(structured.findings,
                     key=lambda f: ["Critical","High","Medium","Low"].index(f.severity)
                     if f.severity in ["Critical","High","Medium","Low"] else 99)
    hs = ParagraphStyle("PH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
    cs = ParagraphStyle("PC", fontSize=8, leading=11, textColor=C_DARK,  fontName="Helvetica")
    rows = [[Paragraph(h, hs) for h in ["#", "Vulnerability", "Severity"]]]
    cw = [10*mm, CW - 30*mm, 20*mm]
    for rank, f in enumerate(ordered[:15], 1):
        rows.append([Paragraph(str(rank), cs), Paragraph(_safe(f.type), cs),
                     Paragraph(f.severity, ParagraphStyle(f"PS{rank}", fontSize=8, leading=10,
                                                           textColor=SEV.get(f.severity, C_GRAY),
                                                           fontName="Helvetica-Bold"))])
    t = Table(rows, colWidths=cw); t.setStyle(table_style())
    story.append(t); story.append(PageBreak()); return story


def _recommendations(structured):
    st = _S()
    story = [*section_title("09  Recommendations"), _sp(4)]
    recs = list({f.recommendation for f in structured.findings if f.recommendation})
    if not recs:
        story.append(Paragraph("No specific recommendations available.", st["Body"]))
    for i, rec in enumerate(recs[:20], 1):
        story.append(Paragraph(f"{i}.  {_safe(rec)}", st["Body"])); story.append(_sp(3))
    story.append(PageBreak()); return story


def _compliance(structured):
    st = _S()
    story = [*section_title("10  Compliance & References"), _sp(4)]
    owasp_map = {
        "sql injection": "A03:2021 \u2013 Injection",
        "command injection": "A03:2021 \u2013 Injection",
        "xss": "A03:2021 \u2013 Injection",
        "hardcoded": "A02:2021 \u2013 Cryptographic Failures",
        "secret": "A02:2021 \u2013 Cryptographic Failures",
        "path traversal": "A01:2021 \u2013 Broken Access Control",
        "depend": "A06:2021 \u2013 Vulnerable Components",
    }
    hs = ParagraphStyle("CH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
    cs = ParagraphStyle("CC", fontSize=8, leading=11, textColor=C_DARK,  fontName="Helvetica")
    rows = [[Paragraph(h, hs) for h in ["Finding Type", "OWASP Top 10", "CWE Reference"]]]
    cw = [CW*0.35, CW*0.40, CW*0.25]; seen = set()
    for f in structured.findings:
        if f.type in seen: continue
        seen.add(f.type)
        owasp = next((v for k, v in owasp_map.items() if k in f.type.lower()), "\u2014")
        rows.append([Paragraph(_safe(f.type), cs), Paragraph(owasp, cs), Paragraph("\u2014", cs)])
    t = Table(rows, colWidths=cw); t.setStyle(table_style())
    story.append(t); story.append(_sp(8))
    story.append(Paragraph(
        "References: OWASP Top 10 (2021) \u00b7 NIST NVD \u00b7 MITRE CWE \u00b7 CVE Database",
        st["Body_Small"]))
    return story


# ── public API — unchanged signatures ────────────────────────────────────────

def _get_scan_or_404(db, scan_id):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


def get_report(db, scan_id):
    scan = _get_scan_or_404(db, scan_id)
    return Report(
        scan_id=scan.id, file_name=scan.file_name, display_file_name=scan.file_name,
        scan_date=scan.scan_date, total_vulnerabilities=getattr(scan, "total_findings", 0),
        risk_score=getattr(scan, "risk_score", 0.0), security_score=getattr(scan, "security_score", 0.0),
        critical_count=getattr(scan, "critical_count", 0), high_count=getattr(scan, "high_count", 0),
        medium_count=getattr(scan, "medium_count", 0), low_count=getattr(scan, "low_count", 0),
        risk_level=risk_level(scan.risk_score), vulnerabilities=list(scan.vulnerabilities),
    )


def get_structured_report(db, scan_id):
    scan = _get_scan_or_404(db, scan_id)
    return build_structured_report(scan)


def get_report_pdf(db, scan_id):
    scan = _get_scan_or_404(db, scan_id)
    structured = build_structured_report(scan)
    buffer = BytesIO()
    doc = _Doc(buffer, scan_id=str(scan.id), file_name=scan.file_name or "",
               pagesize=A4, leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)
    toc = [
        ("01", "Executive Summary"), ("02", "Scan Scope"),    ("03", "Risk Overview"),
        ("04", "AI Insights"),       ("05", "Detailed Findings"), ("06", "Secret Exposure"),
        ("07", "Dependency Vulnerabilities"), ("08", "Risk Prioritization"),
        ("09", "Recommendations"),   ("10", "Compliance & References"),
    ]
    story: List = [
        NextPageTemplate("Cover"), *_cover(scan, structured),
        NextPageTemplate("Inner"), *_toc(toc),
        *_exec_summary(scan, structured), *_scan_scope(scan),
        *_risk_overview(structured),      *_ai_insights(structured),
        *_findings(structured),           *_secrets(structured),
        *_deps(structured),               *_prioritization(structured),
        *_recommendations(structured),    *_compliance(structured),
    ]
    doc.build(story)
    return buffer.getvalue()
