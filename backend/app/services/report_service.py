"""DristiScan PDF Report Generator --- clean, white, professional audit layout."""
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from ..models.scan_model import Scan
from ..schemas.report_schema import FullStructuredReportSchema, Report
from .risk_engine import risk_level
from .structured_report import build_structured_report

logger = logging.getLogger("dristi-scan")

# ------ page geometry ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
PW, PH = A4
ML, MR = 22 * mm, 22 * mm
MT, MB = 28 * mm, 22 * mm
CW = PW - ML - MR  # content width

# ------ color palette (light, print-friendly) ---------------------------------------------------------------------------------------------------------------
C_BLACK = colors.HexColor("#111827")   # headings
C_DARK = colors.HexColor("#374151")    # body
C_GRAY = colors.HexColor("#6B7280")    # secondary
C_LGRAY = colors.HexColor("#D1D5DB")   # borders
C_XLGRAY = colors.HexColor("#F9FAFB")  # row tint
C_WHITE = colors.white
C_BLUE = colors.HexColor("#1D4ED8")    # accent
C_BLUE_LT = colors.HexColor("#EFF6FF") # subtle blue tint
C_BLUE_BD = colors.HexColor("#BFDBFE") # blue border

SEV = {
    "Critical": colors.HexColor("#DC2626"),
    "High": colors.HexColor("#EA580C"),
    "Medium": colors.HexColor("#D97706"),
    "Low": colors.HexColor("#16A34A"),
}
SEV_BG = {
    "Critical": colors.HexColor("#FEF2F2"),
    "High": colors.HexColor("#FFF7ED"),
    "Medium": colors.HexColor("#FFFBEB"),
    "Low": colors.HexColor("#F0FDF4"),
}

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "screens", "logo.png")


def _resolve_logo():
    """Return the first existing logo path to keep branding reliable."""
    candidates = [
        LOGO_PATH,
        os.path.join(os.getcwd(), "docs", "screens", "logo.png"),
        os.path.join(os.path.dirname(__file__), "..", "..", "docs", "screens", "logo.png"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

# ------ styles ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
_SC = None


def _styles():
    """Lazy style registry so everything shares consistent typography."""
    global _SC
    if _SC:
        return _SC

    base = getSampleStyleSheet()
    add = lambda name, **kw: base.add(ParagraphStyle(name=name, **kw)) if name not in base else None

    add("Cover_Title", fontSize=26, leading=32, textColor=C_BLACK, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    add("Cover_Tag", fontSize=12, leading=16, textColor=C_BLUE, fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6)
    add("Cover_Sub", fontSize=10, leading=14, textColor=C_GRAY, fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4)

    add("Sec_Title", fontSize=14, leading=18, textColor=C_BLUE, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4)
    add("Sub_Title", fontSize=11, leading=14, textColor=C_BLACK, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)
    add("Body", fontSize=9, leading=13, textColor=C_DARK, fontName="Helvetica", spaceAfter=4)
    add("Body_Small", fontSize=8, leading=12, textColor=C_GRAY, fontName="Helvetica", spaceAfter=2)
    add("Code", fontSize=8, leading=12, textColor=C_BLACK, fontName="Courier", spaceAfter=4, leftIndent=4)
    add("Label", fontSize=7, leading=10, textColor=C_GRAY, fontName="Helvetica-Bold", spaceAfter=1, spaceBefore=4)
    add("TOC_Entry", fontSize=9, leading=14, textColor=C_DARK, fontName="Helvetica", spaceAfter=2)

    _SC = base
    return base


# ------ helpers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def _sp(h=6):
    return Spacer(1, h)


def _safe(text):
    return escape(str(text or ""))


def _rule(width="100%", color=None, thick=0.5):
    return HRFlowable(width=width, thickness=thick, color=color or C_LGRAY, spaceAfter=6, spaceBefore=2)


def section_title(text):
    """Section heading with thin divider."""
    st = _styles()
    return [Paragraph(text, st["Sec_Title"]), _rule(thick=0.75, color=C_BLUE)]


def code_block(code):
    """Light monospace block --- no dark backgrounds."""
    st = _styles()
    if not code or not str(code).strip():
        return Paragraph("N/A", st["Body_Small"])

    lines = str(code).strip().splitlines()[:50]
    cell = Paragraph(_safe("\n".join(lines)), st["Code"])
    table = Table([[cell]], colWidths=[CW])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F5")),
                ("BOX", (0, 0), (-1, -1), 0.5, C_LGRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def info_card(label, value):
    """Single label/value row with light underline."""
    st = _styles()
    table = Table(
        [[Paragraph(_safe(label), st["Label"]), Paragraph(_safe(value), st["Body"])]],
        colWidths=[50 * mm, CW - 50 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, C_LGRAY),
            ]
        )
    )
    return table


def sev_badge(sev):
    """Inline severity badge --- colored text on very light tint."""
    color = SEV.get(sev, C_GRAY)
    bg = SEV_BG.get(sev, C_WHITE)
    style = ParagraphStyle(
        "SB", fontSize=7, leading=9, textColor=color, fontName="Helvetica-Bold", alignment=TA_CENTER
    )
    table = Table([[Paragraph(sev.upper(), style)]], colWidths=[20 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.5, color),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def table_style():
    """Clean table grid with alternating light shading."""
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), C_BLACK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_XLGRAY]),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, C_LGRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
    )


def draw_header(canvas, file_name):
    """Top-left logo + title, thin underline."""
    logo = _resolve_logo()
    x, y = ML, PH - 15 * mm
    if logo and os.path.exists(logo):
        try:
            canvas.drawImage(logo, x, y - 8 * mm, width=10 * mm, height=10 * mm, mask="auto", preserveAspectRatio=True, anchor='sw')
            x += 12 * mm
        except Exception as exc:  # pragma: no cover
            logger.warning("Header logo failed to render: %s", exc)

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(C_BLUE)
    canvas.drawString(x, y, "DristiScan")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(C_GRAY)
    canvas.drawString(x + 28 * mm, y, "Security Analysis Report")

    canvas.setStrokeColor(C_LGRAY)
    canvas.setLineWidth(0.5)
    canvas.line(ML, y - 3 * mm, PW - MR, y - 3 * mm)

    fn = (file_name or "")[:55]
    canvas.setFillColor(C_GRAY)
    canvas.drawRightString(PW - MR, y, fn)


def draw_footer(canvas, page_no, scan_id):
    """Bottom footer with page number and confidentiality notice."""
    canvas.setStrokeColor(C_LGRAY)
    canvas.line(ML, MB + 8 * mm, PW - MR, MB + 8 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(C_GRAY)
    canvas.drawString(ML, MB + 4 * mm, "Confidential - DristiScan")
    canvas.drawRightString(PW - MR, MB + 4 * mm, f"Page {page_no}")


# ------ document chrome ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class _Doc(BaseDocTemplate):
    def __init__(self, buf, scan_id, file_name, **kw):
        super().__init__(buf, **kw)
        self._sid = scan_id
        self._fn = file_name

        cover = Frame(ML, MB, CW, PH - MT - MB, id="cover")
        inner = Frame(ML, MB + 12 * mm, CW, PH - MT - MB - 12 * mm, id="inner")

        self.addPageTemplates(
            [
                PageTemplate(id="Cover", frames=[cover], onPage=self._cover_bg),
                PageTemplate(id="Inner", frames=[inner], onPage=self._inner_chrome),
            ]
        )

    def _cover_bg(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
        canvas.setFillColor(C_BLUE)
        canvas.rect(0, 0, PW, 3 * mm, fill=1, stroke=0)  # thin accent bar
        canvas.restoreState()

    def _inner_chrome(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)

        draw_header(canvas, self._fn)
        draw_footer(canvas, doc.page, self._sid)
        canvas.restoreState()


# ------ sections ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def _cover(scan, structured):
    st = _styles()
    summary = structured.summary

    risk_label = summary.overall_risk
    risk_color = SEV.get(risk_label, C_GRAY)
    risk_bg = SEV_BG.get(risk_label, C_WHITE)
    scan_date = getattr(scan, "scan_date", datetime.utcnow())
    date_str = scan_date.strftime("%B %d, %Y") if hasattr(scan_date, "strftime") else str(scan_date)

    story = [_sp(20)]

    logo = _resolve_logo()
    if logo and os.path.exists(logo):
        img = Image(logo, width=40 * mm, height=40 * mm, mask="auto")
        story.append(Table([[img]], colWidths=[CW], style=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        story.append(_sp(10))

    story += [
        Paragraph("DristiScan", st["Cover_Title"]),
        Paragraph("Intelligent DevSecOps Security Platform", st["Cover_Tag"]),
        Paragraph("Security Analysis Report", st["Cover_Sub"]),
        _sp(6),
        _rule(thick=1, color=C_BLUE),
        _sp(10),
        Paragraph(
            _safe(scan.file_name or "Unknown Target"),
            ParagraphStyle(
                "CFile",
                fontSize=13,
                leading=17,
                textColor=C_BLACK,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                spaceAfter=4,
            ),
        ),
    ]

    meta = ParagraphStyle(
        "CMeta", fontSize=9, leading=13, textColor=C_GRAY, fontName="Helvetica", alignment=TA_CENTER, spaceAfter=3
    )
    story += [Paragraph(f"Scan ID: #{scan.id}", meta), Paragraph(f"Date: {date_str}", meta), _sp(14)]

    badge_style = ParagraphStyle(
        "CBadge", fontSize=12, leading=16, textColor=risk_color, fontName="Helvetica-Bold", alignment=TA_CENTER
    )
    badge = Table([[Paragraph(f"{risk_label.upper()} RISK", badge_style)]], colWidths=[50 * mm])
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), risk_bg),
                ("BOX", (0, 0), (-1, -1), 1.2, risk_color),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(Table([[badge]], colWidths=[CW], style=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(_sp(16))

    counts = ParagraphStyle(
        "CCnt", fontSize=9, leading=13, textColor=C_GRAY, fontName="Helvetica", alignment=TA_CENTER
    )
    story.append(
        Paragraph(
            f"Total Findings: {summary.total} -- Critical: {summary.critical} -- High: {summary.high} -- "
            f"Medium: {summary.medium} -- Low: {summary.low}",
            counts,
        )
    )
    story.append(PageBreak())
    return story


def _toc(sections):
    st = _styles()
    story = [*section_title("Table of Contents"), _sp(6)]
    for num, title in sections:
        row = Table(
            [[Paragraph(num, st["Body_Small"]), Paragraph(title, st["TOC_Entry"])]],
            colWidths=[12 * mm, CW - 12 * mm],
        )
        row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.25, C_LGRAY),
                ]
            )
        )
        story.append(row)
    story.append(PageBreak())
    return story


def _exec_summary(scan, structured):
    st = _styles()
    summary = structured.summary
    rs = structured.risk_score
    sec_score = max(0.0, 100.0 - rs.score * 10)
    scan_date = getattr(scan, "scan_date", datetime.utcnow())
    date_str = scan_date.strftime("%Y-%m-%d %H:%M UTC") if hasattr(scan_date, "strftime") else str(scan_date)

    story = [*section_title("01  Executive Summary"), _sp(8)]

    # Severity grid (borders only, no fills)
    cw4 = CW / 4
    header = ParagraphStyle("ESH", fontSize=8, leading=10, textColor=C_GRAY, fontName="Helvetica-Bold", alignment=TA_CENTER)
    value = ParagraphStyle("ESV", fontSize=22, leading=26, fontName="Helvetica-Bold", alignment=TA_CENTER)
    data = [
        [Paragraph("CRITICAL", header), Paragraph("HIGH", header), Paragraph("MEDIUM", header), Paragraph("LOW", header)],
        [
            Paragraph(str(summary.critical), ParagraphStyle("ESC", parent=value, textColor=SEV["Critical"])),
            Paragraph(str(summary.high), ParagraphStyle("ESH2", parent=value, textColor=SEV["High"])),
            Paragraph(str(summary.medium), ParagraphStyle("ESM", parent=value, textColor=SEV["Medium"])),
            Paragraph(str(summary.low), ParagraphStyle("ESL", parent=value, textColor=SEV["Low"])),
        ],
    ]
    sev_table = Table(data, colWidths=[cw4] * 4)
    sev_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, C_LGRAY),
                ("LINEAFTER", (0, 0), (2, -1), 0.25, C_LGRAY),
                ("LINEBELOW", (0, 0), (-1, 0), 0.25, C_LGRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(sev_table)
    story.append(_sp(10))

    for label, value_text in [
        ("Total Findings", str(summary.total)),
        ("Overall Risk", summary.overall_risk),
        ("Risk Score", f"{rs.score:.1f} / 10"),
        ("Security Score", f"{sec_score:.0f} / 100"),
        ("Scan Date", date_str),
        ("Target", scan.file_name or "Unknown"),
    ]:
        story.append(info_card(label, value_text))
    story.append(_sp(6))
    if rs.reason:
        story.append(Paragraph(f"<b>Risk Rationale:</b> {_safe(rs.reason)}", st["Body"]))
    story.append(PageBreak())
    return story


def _scan_scope(scan):
    st = _styles()
    story = [*section_title("02  Scan Scope"), _sp(6)]
    for label, value in [
        ("Target File / Repo", scan.file_name or "Unknown"),
        ("Scan Engine", "DristiScan v2 - Rule Engine + AI Agents"),
        ("Scan Type", "Static Application Security Testing (SAST)"),
        ("Scan Date", str(getattr(scan, "scan_date", "N/A"))),
        ("Total Issues", str(getattr(scan, "total_findings", 0))),
    ]:
        story.append(info_card(label, value))
    story.append(_sp(4))
    story.append(
        Paragraph(
            "This report covers static analysis of the submitted source code. Dynamic testing, penetration testing, and runtime analysis are outside scope.",
            st["Body"],
        )
    )
    story.append(PageBreak())
    return story


def _risk_overview(structured):
    st = _styles()
    summary = structured.summary
    story = [*section_title("03  Risk Overview"), _sp(6)]
    cat_counts = Counter(f.type for f in structured.findings)
    if cat_counts:
        total = max(summary.total, 1)
        head = ParagraphStyle("ROH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
        cell = ParagraphStyle("ROC", fontSize=8, leading=11, textColor=C_DARK, fontName="Helvetica")
        rows = [[Paragraph(h, head) for h in ["Vulnerability Type", "Count", "% of Total"]]]
        for vtype, cnt in cat_counts.most_common():
            rows.append(
                [Paragraph(_safe(vtype), cell), Paragraph(str(cnt), cell), Paragraph(f"{cnt/total*100:.0f}%", cell)]
            )
        table = Table(rows, colWidths=[CW * 0.6, CW * 0.2, CW * 0.2])
        table.setStyle(table_style())
        story.append(table)
    story.append(PageBreak())
    return story


def _ai_insights(structured):
    st = _styles()
    ins = structured.ai_insights
    story = [*section_title("04  AI Insights"), _sp(6)]
    cell_style = ParagraphStyle(
        "AIH", fontSize=9, leading=13, textColor=C_DARK, fontName="Helvetica", leftIndent=8, rightIndent=8
    )
    for label, value in [
        ("Analysis Summary", ins.summary),
        ("Most Critical Issue", ins.most_critical_issue),
        ("Recommended Fix Priority", ins.fix_priority),
    ]:
        if not value:
            continue
        story.append(Paragraph(label.upper(), st["Label"]))
        cell = Table([[Paragraph(_safe(value), cell_style)]], colWidths=[CW])
        cell.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), C_BLUE_LT),
                    ("BOX", (0, 0), (-1, -1), 0.75, C_BLUE_BD),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.extend([cell, _sp(8)])
    story.append(PageBreak())
    return story


def _findings(structured):
    st = _styles()
    findings = structured.findings
    story = [*section_title("05  Detailed Findings"), _sp(6)]
    if not findings:
        story.append(Paragraph("No vulnerabilities detected.", st["Body"]))
        story.append(PageBreak())
        return story

    seen = set()
    deduped = []
    for finding in findings:
        key = (finding.type, finding.line)
        if key not in seen:
            seen.add(key)
            deduped.append(finding)

    for idx, finding in enumerate(deduped, 1):
        sev = finding.severity
        num = ParagraphStyle(f"FN{idx}", fontSize=9, leading=11, textColor=C_GRAY, fontName="Helvetica-Bold")
        title = ParagraphStyle(f"FT{idx}", fontSize=11, leading=14, textColor=C_BLACK, fontName="Helvetica-Bold")
        header = Table(
            [[Paragraph(f"{idx:02d}", num), Paragraph(_safe(finding.type), title), sev_badge(sev)]],
            colWidths=[10 * mm, CW - 30 * mm, 20 * mm],
        )
        header.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(header)
        story.append(_sp(3))
        if finding.line:
            story.append(Paragraph(f"File / Line: {finding.line}", st["Body_Small"]))
        story.append(_rule(thick=0.25))
        story.append(_sp(3))

        for label, value in [
            ("Description", finding.description),
            ("Impact", finding.impact),
            ("Attack Example", finding.attack_example),
            ("Recommendation", finding.recommendation),
            ("OWASP / CWE / CVE", " / ".join(filter(None, [
                getattr(finding, "owasp", None),
                getattr(finding, "cwe", None),
                getattr(finding, "cve", None),
            ])) or "N/A"),
        ]:
            if value and str(value).strip():
                story.append(Paragraph(label.upper(), st["Label"]))
                story.append(Paragraph(_safe(value), st["Body"]))
                story.append(_sp(2))

        if finding.code and str(finding.code).strip():
            story.append(Paragraph("AFFECTED CODE", st["Label"]))
            story.append(code_block(finding.code))
            story.append(_sp(3))
        if finding.fix_code and str(finding.fix_code).strip():
            story.append(Paragraph("SECURE CODE EXAMPLE", st["Label"]))
            story.append(code_block(finding.fix_code))
            story.append(_sp(3))

        story.append(_rule(thick=0.5, color=C_LGRAY))
        story.append(_sp(8))

    story.append(PageBreak())
    return story


def _secrets(structured):
    st = _styles()
    secrets = [
        f
        for f in structured.findings
        if any(key in f.type.lower() for key in ("secret", "key", "credential", "token", "password"))
    ]
    if not secrets:
        return []

    story = [*section_title("06  Secret Exposure"), _sp(4)]
    story.append(Paragraph(f"{len(secrets)} hardcoded secret(s) detected. Rotate all exposed credentials immediately.", st["Body"]))
    story.append(_sp(6))
    for sf in secrets:
        story.append(Paragraph(f"> {_safe(sf.type)}", st["Sub_Title"]))
        for label, value in [
            ("Severity", sf.severity),
            ("Line", str(sf.line) if sf.line else "N/A"),
            ("Recommendation", sf.recommendation or "Rotate and move to a secrets manager."),
        ]:
            story.append(info_card(label, value))
        story.append(_sp(6))
    story.append(PageBreak())
    return story


def _deps(structured):
    st = _styles()
    deps = [f for f in structured.findings if any(key in f.type.lower() for key in ("depend", "package", "library", "cve"))]
    if not deps:
        return []

    story = [*section_title("07  Dependency Vulnerabilities"), _sp(4)]
    head = ParagraphStyle("DH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
    cell = ParagraphStyle("DC", fontSize=8, leading=11, textColor=C_DARK, fontName="Helvetica")
    rows = [[Paragraph(h, head) for h in ["Package / Type", "Severity", "Description", "Fix"]]]
    widths = [CW * 0.25, CW * 0.12, CW * 0.38, CW * 0.25]
    for dep in deps:
        rows.append(
            [
                Paragraph(_safe(dep.type), cell),
                Paragraph(_safe(dep.severity), cell),
                Paragraph(_safe(dep.description[:120]), cell),
                Paragraph(_safe(dep.recommendation[:80]), cell),
            ]
        )
    table = Table(rows, colWidths=widths)
    table.setStyle(table_style())
    story.append(table)
    story.append(PageBreak())
    return story


def _prioritization(structured):
    st = _styles()
    story = [*section_title("08  Risk Prioritization"), _sp(4)]
    story.append(Paragraph("Address findings in the following order:", st["Body"]))
    story.append(_sp(6))

    ordered = sorted(
        structured.findings,
        key=lambda f: ["Critical", "High", "Medium", "Low"].index(f.severity)
        if f.severity in ["Critical", "High", "Medium", "Low"]
        else 99,
    )
    head = ParagraphStyle("PH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
    cell = ParagraphStyle("PC", fontSize=8, leading=11, textColor=C_DARK, fontName="Helvetica")
    rows = [[Paragraph(h, head) for h in ["#", "Vulnerability", "Severity"]]]
    widths = [10 * mm, CW - 30 * mm, 20 * mm]
    for rank, finding in enumerate(ordered[:15], 1):
        rows.append(
            [
                Paragraph(str(rank), cell),
                Paragraph(_safe(finding.type), cell),
                Paragraph(
                    finding.severity,
                    ParagraphStyle(
                        f"PS{rank}",
                        fontSize=8,
                        leading=10,
                        textColor=SEV.get(finding.severity, C_GRAY),
                        fontName="Helvetica-Bold",
                    ),
                ),
            ]
        )
    table = Table(rows, colWidths=widths)
    table.setStyle(table_style())
    story.append(table)
    story.append(PageBreak())
    return story


def _recommendations(structured):
    st = _styles()
    story = [*section_title("09  Recommendations"), _sp(4)]
    recs = list({f.recommendation for f in structured.findings if f.recommendation})
    if not recs:
        story.append(Paragraph("No specific recommendations available.", st["Body"]))
    for idx, rec in enumerate(recs[:20], 1):
        story.append(Paragraph(f"{idx}.  {_safe(rec)}", st["Body"]))
        story.append(_sp(3))
    story.append(PageBreak())
    return story


def _compliance(structured):
    st = _styles()
    story = [*section_title("10  Compliance & References"), _sp(4)]
    owasp_map = {
        "sql injection": "A03:2021 - Injection",
        "command injection": "A03:2021 - Injection",
        "xss": "A03:2021 - Injection",
        "hardcoded": "A02:2021 - Cryptographic Failures",
        "secret": "A02:2021 - Cryptographic Failures",
        "path traversal": "A01:2021 - Broken Access Control",
        "depend": "A06:2021 - Vulnerable Components",
    }
    head = ParagraphStyle("CH", fontSize=8, leading=10, textColor=C_BLACK, fontName="Helvetica-Bold")
    cell = ParagraphStyle("CC", fontSize=8, leading=11, textColor=C_DARK, fontName="Helvetica")
    rows = [[Paragraph(h, head) for h in ["Finding Type", "OWASP Top 10", "CWE Reference"]]]
    widths = [CW * 0.35, CW * 0.40, CW * 0.25]
    seen = set()
    for finding in structured.findings:
        if finding.type in seen:
            continue
        seen.add(finding.type)
        owasp = next((val for key, val in owasp_map.items() if key in finding.type.lower()), "-")
        rows.append([Paragraph(_safe(finding.type), cell), Paragraph(owasp, cell), Paragraph("-", cell)])
    table = Table(rows, colWidths=widths)
    table.setStyle(table_style())
    story.append(table)
    story.append(_sp(8))
    story.append(
        Paragraph(
            "References: OWASP Top 10 (2021) -- NIST NVD -- MITRE CWE -- CVE Database",
            st["Body_Small"],
        )
    )
    return story


# ------ public API (signatures unchanged) ----------------------------------------------------------------------------------------------------------------------------
def _get_scan_or_404(db: Session, scan_id: int) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


def get_report(db: Session, scan_id: int) -> Report:
    scan = _get_scan_or_404(db, scan_id)
    return Report(
        scan_id=scan.id,
        file_name=scan.file_name,
        display_file_name=scan.file_name,
        scan_date=scan.scan_date,
        total_vulnerabilities=getattr(scan, "total_findings", 0),
        risk_score=getattr(scan, "risk_score", 0.0),
        security_score=getattr(scan, "security_score", 0.0),
        critical_count=getattr(scan, "critical_count", 0),
        high_count=getattr(scan, "high_count", 0),
        medium_count=getattr(scan, "medium_count", 0),
        low_count=getattr(scan, "low_count", 0),
        risk_level=risk_level(scan.risk_score),
        vulnerabilities=list(scan.vulnerabilities),
    )


def get_structured_report(db: Session, scan_id: int) -> FullStructuredReportSchema:
    scan = _get_scan_or_404(db, scan_id)
    return build_structured_report(scan)


def get_report_pdf(db: Session, scan_id: int) -> bytes:
    scan = _get_scan_or_404(db, scan_id)
    structured = build_structured_report(scan)

    buffer = BytesIO()
    doc = _Doc(
        buffer,
        scan_id=str(scan.id),
        file_name=scan.file_name or "",
        pagesize=A4,
        leftMargin=ML,
        rightMargin=MR,
        topMargin=MT,
        bottomMargin=MB,
    )

    toc = [
        ("01", "Executive Summary"),
        ("02", "Scan Scope"),
        ("03", "Risk Overview"),
        ("04", "AI Insights"),
        ("05", "Detailed Findings"),
        ("06", "Secret Exposure"),
        ("07", "Dependency Vulnerabilities"),
        ("08", "Risk Prioritization"),
        ("09", "Recommendations"),
        ("10", "Compliance & References"),
    ]

    story: List = [
        NextPageTemplate("Cover"),
        *_cover(scan, structured),
        NextPageTemplate("Inner"),
        *_toc(toc),
        *_exec_summary(scan, structured),
        *_scan_scope(scan),
        *_risk_overview(structured),
        *_ai_insights(structured),
        *_findings(structured),
        *_secrets(structured),
        *_deps(structured),
        *_prioritization(structured),
        *_recommendations(structured),
        *_compliance(structured),
    ]

    doc.build(story)
    return buffer.getvalue()
