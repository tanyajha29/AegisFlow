from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape
import logging

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from ..models.scan_model import Scan
from ..schemas.report_schema import FullStructuredReportSchema, Report
from .risk_engine import risk_level
from .structured_report import build_structured_report


THEME_BG = colors.white
TEXT = colors.HexColor("#0f172a")
BADGE_TEXT = colors.white
SEVERITY_COLORS = {
    "Critical": colors.HexColor("#ff4444"),
    "High": colors.HexColor("#ff8800"),
    "Medium": colors.HexColor("#ffcc00"),
    "Low": colors.HexColor("#00cc66"),
}
logger = logging.getLogger("dristi-scan")


def _build_styles():
    styles = getSampleStyleSheet()
    if "ReportTitle" not in styles:
        styles.add(
          ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            textColor=TEXT,
            spaceAfter=12,
          )
        )
    if "Heading" not in styles:
        styles.add(ParagraphStyle(name="Heading", fontSize=16, leading=20, textColor=TEXT, spaceAfter=8))
    if "Body" not in styles:
        styles.add(ParagraphStyle(name="Body", fontSize=11, leading=14, textColor=TEXT))
    if "Badge" not in styles:
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
    if "Code" not in styles:
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
                ("TEXTCOLOR", (0, 0), (-1, -1), BADGE_TEXT),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        ),
    )


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


def _get_scan_or_404(db: Session, scan_id: int) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


def get_structured_report(db: Session, scan_id: int) -> FullStructuredReportSchema:
    scan = _get_scan_or_404(db, scan_id)
    return build_structured_report(scan)


def _summary_section(scan: Scan, structured: FullStructuredReportSchema, styles):
    summary = structured.summary
    data = [
        ["Total Findings", str(summary.total)],
        ["Critical / High / Medium / Low", f"{summary.critical} / {summary.high} / {summary.medium} / {summary.low}"],
        ["Overall Risk", summary.overall_risk],
        ["File / Target", getattr(scan, "file_name", "N/A")],
        ["Scan ID", str(getattr(scan, "id", "N/A"))],
        ["Scan Date", getattr(scan, "scan_date", datetime.utcnow()).strftime("%Y-%m-%d %H:%M")],
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
    badge = _severity_badge(f"{summary.overall_risk} Risk")
    return [Paragraph("Scan Summary", styles["Heading"]), table, Spacer(1, 8), badge, Spacer(1, 12)]


def _vulnerability_details_section(structured: FullStructuredReportSchema, styles):
    story = [Paragraph("Vulnerability Details", styles["Heading"])]
    if not structured.findings:
        story.append(Paragraph("No vulnerabilities detected.", styles["Body"]))
        story.append(Spacer(1, 12))
        return story

    for finding in structured.findings:
        header = Table(
            [
                [
                    Paragraph(finding.type, styles["Body"]),
                    _severity_badge(f"{finding.severity}"),
                ]
            ],
            colWidths=[4.5 * inch, 2 * inch],
            style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TEXTCOLOR", (0, 0), (0, 0), TEXT)],
        )
        meta = Paragraph(f"Line: {finding.line}", styles["Body"])
        snippet = Paragraph(f"<b>Affected Code Snippet</b><br/>{escape(finding.code or 'N/A')}", styles["Code"])
        desc = Paragraph(f"<b>Description</b><br/>{escape(finding.description or 'N/A')}", styles["Body"])
        impact = Paragraph(f"<b>Impact</b><br/>{escape(finding.impact or 'N/A')}", styles["Body"])
        attack = Paragraph(f"<b>Attack Example</b><br/>{escape(finding.attack_example or 'N/A')}", styles["Body"])
        recommendation = Paragraph(f"<b>Recommendation</b><br/>{escape(finding.recommendation or 'N/A')}", styles["Body"])
        fix = Paragraph(f"<b>Fixed Code Example</b><br/>{escape(finding.fix_code or 'N/A')}", styles["Code"])
        story.extend(
            [
                header,
                Spacer(1, 4),
                meta,
                Spacer(1, 4),
                snippet,
                Spacer(1, 6),
                desc,
                Spacer(1, 4),
                impact,
                Spacer(1, 4),
                attack,
                Spacer(1, 4),
                recommendation,
                Spacer(1, 4),
                fix,
                Spacer(1, 12),
            ]
        )
    return story


def _risk_score_section(structured: FullStructuredReportSchema, styles):
    risk = structured.risk_score
    table = Table(
        [["Score (0-10)", f"{risk.score:.2f}"], ["Reason", risk.reason]],
        colWidths=[2.0 * inch, 4.0 * inch],
        style=[
            ("BACKGROUND", (0, 0), (-1, -1), colors.Color(1, 1, 1, alpha=0.03)),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.Color(1, 1, 1, alpha=0.1)),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
    )
    return [Paragraph("Risk Score", styles["Heading"]), table, Spacer(1, 12)]


def _ai_insights_section(structured: FullStructuredReportSchema, styles):
    insights = structured.ai_insights
    return [
        Paragraph("AI Insights", styles["Heading"]),
        Paragraph(f"<b>Summary</b><br/>{escape(insights.summary or 'N/A')}", styles["Body"]),
        Spacer(1, 4),
        Paragraph(f"<b>Most Dangerous Vulnerability</b><br/>{escape(insights.most_critical_issue or 'N/A')}", styles["Body"]),
        Spacer(1, 4),
        Paragraph(f"<b>Suggested Fix Priority</b><br/>{escape(insights.fix_priority or 'N/A')}", styles["Body"]),
        Spacer(1, 12),
    ]


def _secure_code_section(structured: FullStructuredReportSchema, styles):
    secure = structured.secure_version or "Secure code suggestion unavailable."
    return [
        Paragraph("Secure Code Suggestions", styles["Heading"]),
        Paragraph(escape(secure), styles["Code"] if secure else styles["Body"]),
    ]


def get_report_pdf(db: Session, scan_id: int) -> bytes:
    scan = _get_scan_or_404(db, scan_id)
    structured = build_structured_report(scan)
    buffer = BytesIO()
    styles = _build_styles()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=48, bottomMargin=48)

    story = []
    # Cover page
    story.append(Paragraph("DristiScan Security Report", styles["ReportTitle"]))
    story.append(Paragraph(f"File: {scan.file_name}", styles["Body"]))
    story.append(Paragraph(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Body"]))
    story.append(Spacer(1, 12))
    story.append(_severity_badge(f"{structured.summary.overall_risk} Risk"))
    story.append(PageBreak())

    story.extend(_summary_section(scan, structured, styles))
    story.extend(_vulnerability_details_section(structured, styles))
    story.extend(_risk_score_section(structured, styles))
    story.extend(_ai_insights_section(structured, styles))
    story.extend(_secure_code_section(structured, styles))

    doc.build(story, onFirstPage=_apply_background, onLaterPages=_apply_background)
    return buffer.getvalue()
