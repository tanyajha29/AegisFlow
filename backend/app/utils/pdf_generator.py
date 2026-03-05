from fpdf import FPDF

from ..schemas.report_schema import Report


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Dristi-Scan Security Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_pdf(report: Report) -> bytes:
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 8, f"Scan ID: {report.scan_id}", ln=True)
    pdf.cell(0, 8, f"File: {report.file_name}", ln=True)
    pdf.cell(0, 8, f"Scan Date: {report.scan_date}", ln=True)
    pdf.cell(0, 8, f"Risk Score: {report.risk_score}", ln=True)
    if report.risk_level:
        pdf.cell(0, 8, f"Risk Level: {report.risk_level}", ln=True)
    pdf.cell(0, 8, f"Total Vulnerabilities: {report.total_vulnerabilities}", ln=True)
    pdf.ln(4)

    for vuln in report.vulnerabilities:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"{vuln.name} ({vuln.severity})", ln=True)
        pdf.set_font("Helvetica", "", 10)
        if vuln.cwe_reference:
            pdf.cell(0, 6, f"CWE: {vuln.cwe_reference}", ln=True)
        if vuln.line_number:
            pdf.cell(0, 6, f"Line: {vuln.line_number}", ln=True)
        pdf.multi_cell(0, 6, f"Description: {vuln.description}")
        pdf.multi_cell(0, 6, f"Remediation: {vuln.remediation}")
        if vuln.code_snippet:
            pdf.multi_cell(0, 6, f"Snippet: {vuln.code_snippet}")
        pdf.ln(2)

    return pdf.output(dest="S")
