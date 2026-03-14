from collections import defaultdict
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from ..models.scan_model import Scan
from ..schemas.report_schema import Report
from .risk_engine import risk_level
from .ai_summary import generate_ai_insight


THEME_BG = colors.HexColor("#0d1117")
TEXT = colors.HexColor("#e6edf3")
SEVERITY_COLORS = {
    "Critical": colors.HexColor("#ff4444"),
    "High": colors.HexColor("#ff8800"),
    "Medium": colors.HexColor("#ffcc00"),
    "Low": colors.HexColor("#00cc66"),
}


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Title", fontSize=22, leading=26, textColor=TEXT, spaceAfter=12))
    styles.add(ParagraphStyle(name="Heading", fontSize=16, leading=20, textColor=TEXT, spaceAfter=8))
    styles.add(ParagraphStyle(name="Body", fontSize=11, leading=14, textColor=TEXT))
    styles.add(
        ParagraphStyle(
            name="Badge",
            fontSize=10,
            leading=12,
            textColor=TEXT,
            alignment=1,
            padding=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Code",
            fontName="Courier",
            fontSize=9,
            leading=12,
            textColor=TEXT,
            backColor=colors.Color(0, 0, 0, alpha=0.15),
        )
    )
    return styles


def _apply_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(THEME_BG)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.restoreState()


def _severity_badge(text: str):
    return Table(
        [[Paragraph(text, _build_styles()["Badge"])]],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SEVERITY_COLORS.get(text.split()[0], TEXT)),
                ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        ),
    )


def get_report(db: Session, scan_id: int) -> Report:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return Report(
        scan_id=scan.id,
        file_name=scan.file_name,
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


def _exec_summary(report: Report, styles):
    data = [
        ["Security Score", f"{report.security_score:.0f}"],
        ["Risk Score", f"{report.risk_score:.0f}"],
        ["Total Findings", str(report.total_vulnerabilities)],
        ["Critical / High / Medium / Low", f"{report.critical_count} / {report.high_count} / {report.medium_count} / {report.low_count}"],
    ]
    table = Table(
        data,
        colWidths=[2.5 * inch, 3.5 * inch],
        style=[
            ("BACKGROUND", (0, 0), (-1, -1), colors.Color(1, 1, 1, alpha=0.03)),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
    )
    badge = _severity_badge(report.risk_level or "Unknown Risk")
    return [Paragraph("Executive Summary", styles["Heading"]), table, Spacer(1, 8), badge, Spacer(1, 12)]


def _scan_information(report: Report, styles):
    info = [
        ["File / Target", report.file_name],
        ["Scan ID", str(report.scan_id)],
        ["Scan Date", report.scan_date.strftime("%Y-%m-%d %H:%M")],
        ["Engine", "DristiScan Orchestrator v2"],
    ]
    table = Table(
        info,
        colWidths=[2.0 * inch, 4.0 * inch],
        style=[
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
            ("BACKGROUND", (0, 0), (-1, -1), colors.Color(1, 1, 1, alpha=0.02)),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
    )
    return [Paragraph("Scan Information", styles["Heading"]), table, Spacer(1, 10)]


def _findings_section(report: Report, styles):
    story = [Paragraph("Vulnerability Findings", styles["Heading"])]
    for vuln in report.vulnerabilities:
        sev_color = SEVERITY_COLORS.get(vuln.severity, TEXT)
        header = Table(
            [
                [
                    Paragraph(f"{vuln.name}", styles["Body"]),
                    _severity_badge(f"{vuln.severity} Risk"),
                ]
            ],
            colWidths=[4.5 * inch, 2 * inch],
            style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TEXTCOLOR", (0, 0), (0, 0), TEXT)],
        )
        meta = Paragraph(
            f"<font color='{sev_color}'>File:</font> {escape(vuln.file_name or 'N/A')} | Line: {vuln.line_number or 'N/A'}",
            styles["Body"],
        )
        snippet = Paragraph(f"<b>Code Snippet</b><br/>{escape(vuln.code_snippet or 'N/A')}", styles["Code"])
        desc = Paragraph(f"<b>Description</b><br/>{escape(vuln.description or 'N/A')}", styles["Body"])
        remediation = Paragraph(f"<b>Remediation</b><br/>{escape(vuln.remediation or 'N/A')}", styles["Body"])
        cwe = Paragraph(f"<b>CWE</b>: {escape(vuln.cwe_reference or 'N/A')}", styles["Body"])
        story.extend([header, Spacer(1, 4), meta, Spacer(1, 4), snippet, Spacer(1, 6), desc, Spacer(1, 4), remediation, Spacer(1, 4), cwe, Spacer(1, 12)])
    return story


def _remediation_summary(report: Report, styles):
    remediation_map: dict[str, set] = defaultdict(set)
    for vuln in report.vulnerabilities:
        remediation_map[vuln.severity].add(vuln.remediation or "Review and fix the issue.")
    rows = [["Severity", "Recommended Actions"]]
    for severity in ("Critical", "High", "Medium", "Low"):
        if severity not in remediation_map:
            continue
        actions = "<br/>".join(f"- {item}" for item in sorted(remediation_map[severity]))
        rows.append([severity, actions])
    if len(rows) == 1:
        rows.append(["All", "No remediations recorded."])
    table = Table(
        rows,
        colWidths=[1.5 * inch, 4.5 * inch],
        style=[
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(1, 1, 1, alpha=0.08)),
            ("BACKGROUND", (0, 1), (-1, -1), colors.Color(1, 1, 1, alpha=0.03)),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
    )
    return [Paragraph("Remediation Summary", styles["Heading"]), table]


def get_report_pdf(db: Session, scan_id: int) -> bytes:
    report = get_report(db, scan_id)
    ai_insight = generate_ai_insight(report)
    buffer = BytesIO()
    styles = _build_styles()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=48, bottomMargin=48)

    story = []
    # Cover page
    story.append(Paragraph("DristiScan Security Report", styles["Title"]))
    story.append(Paragraph(f"File: {report.file_name}", styles["Body"]))
    story.append(Paragraph(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Body"]))
    story.append(Spacer(1, 12))
    story.append(_severity_badge(report.risk_level or "Risk"))
    story.append(PageBreak())

    story.extend(_exec_summary(report, styles))
    story.extend(_scan_information(report, styles))
    if ai_insight:
        story.append(Paragraph("AI Executive Insight", styles["Heading"]))
        story.append(Paragraph(ai_insight.replace("\n", "<br/>"), styles["Body"]))
        story.append(Spacer(1, 12))
    story.extend(_findings_section(report, styles))
    story.append(PageBreak())
    story.extend(_remediation_summary(report, styles))

    doc.build(story, onFirstPage=_apply_background, onLaterPages=_apply_background)
    return buffer.getvalue()
