"""ReportLab PDF Exporter for ThreatVision AI Incident Summaries."""

from pathlib import Path
from typing import Any, Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReportExporter:
    """Generates PDF reports for security incident audits."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self, incident_data: Dict[str, Any], filename: str | None = None
    ) -> str:
        """Generate PDF report from incident data dictionary."""
        incident_id = incident_data.get("incident_id", "INCIDENT")
        pdf_name = filename or f"Report_{incident_id}.pdf"
        pdf_path = self.output_dir / pdf_name

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
        )
        subtitle_style = ParagraphStyle(
            "SubtitleStyle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748B"),
        )

        elements = []
        elements.append(Paragraph("THREATVISION AI — INCIDENT SAFETY REPORT", title_style))
        elements.append(Paragraph(f"Generated for Incident ID: {incident_id}", subtitle_style))
        elements.append(Spacer(1, 15))

        # Summary Table
        table_data = [
            ["Attribute", "Details"],
            ["Timestamp", incident_data.get("timestamp", "N/A")],
            ["Threat Level", incident_data.get("threat_level", "N/A")],
            ["Threat Score", f"{int(incident_data.get('threat_score', 0) * 100)}%"],
            ["Primary Threat", incident_data.get("primary_threat", "N/A")],
            ["Camera ID", incident_data.get("camera_id", "0")],
            ["Recommendation", incident_data.get("recommendation", "N/A")],
        ]

        t = Table(table_data, colWidths=[150, 380])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#1E293B")),
                    ("TEXTCOLOR", (0, 0), (1, 0), colors.white),
                    ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ]
            )
        )
        elements.append(t)
        elements.append(Spacer(1, 15))

        # Include Screenshot Image if available
        screenshot_path = incident_data.get("screenshot_path")
        if screenshot_path and Path(screenshot_path).exists():
            elements.append(Paragraph("Incident Frame Snapshot:", styles["Heading2"]))
            elements.append(Spacer(1, 5))
            try:
                img = RLImage(screenshot_path, width=450, height=250)
                elements.append(img)
            except Exception:
                pass

        doc.build(elements)
        return str(pdf_path)
