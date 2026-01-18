import io
import logging
from pathlib import Path

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF documents."""

    @staticmethod
    def generate_exam_result_pdf(attempt, institution=None):
        """
        Generate a PDF document for an exam result.

        Args:
            attempt: ExamAttempt instance
            institution: Institution instance (optional)

        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=6,
            alignment=1,  # Center
        )
        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=12,
            spaceAfter=12,
            alignment=1,  # Center
            textColor=colors.grey,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
        )

        # Build document elements
        elements = []

        # Institution Header
        if institution:
            # Try to add logo if it exists
            if institution.logo:
                try:
                    logo_path = Path(settings.MEDIA_ROOT) / str(institution.logo)
                    if logo_path.exists():
                        img = Image(str(logo_path), width=1.5 * inch, height=1.5 * inch)
                        img.hAlign = "CENTER"
                        elements.append(img)
                        elements.append(Spacer(1, 6))
                except Exception as e:
                    logger.warning(f"Could not load institution logo: {e}")

            elements.append(Paragraph(institution.name, title_style))
            if institution.address:
                elements.append(
                    Paragraph(
                        institution.address.replace("\n", "<br/>"), subtitle_style
                    )
                )
            elements.append(Spacer(1, 12))

        # Document Title
        elements.append(Paragraph("Exam Result Certificate", title_style))
        elements.append(Spacer(1, 20))

        # Student Information Section
        elements.append(Paragraph("Student Information", heading_style))
        student = attempt.student
        student_data = [
            ["Name:", student.get_full_name() or student.username],
            ["Email:", student.email],
        ]
        if student.assigned_class:
            student_data.append(["Class:", student.assigned_class.name])

        student_table = Table(student_data, colWidths=[100, 350])
        student_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(student_table)
        elements.append(Spacer(1, 20))

        # Exam Information Section
        elements.append(Paragraph("Exam Information", heading_style))
        exam = attempt.exam
        exam_data = [
            ["Exam Title:", exam.title],
            ["Subject:", exam.subject.name],
            ["Duration:", exam.duration_display],
            ["Total Questions:", str(attempt.total_questions)],
        ]

        exam_table = Table(exam_data, colWidths=[100, 350])
        exam_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(exam_table)
        elements.append(Spacer(1, 20))

        # Result Section
        elements.append(Paragraph("Result", heading_style))

        # Score display
        percentage = attempt.percentage_score
        status = "PASSED" if percentage >= 50 else "FAILED"
        status_color = colors.green if percentage >= 50 else colors.red

        result_data = [
            ["Score:", f"{attempt.score} / {attempt.total_questions}"],
            ["Percentage:", f"{percentage}%"],
            ["Status:", status],
            ["Started At:", attempt.started_at.strftime("%b %d, %Y at %H:%M")],
            [
                "Submitted At:",
                (
                    attempt.submitted_at.strftime("%b %d, %Y at %H:%M")
                    if attempt.submitted_at
                    else "N/A"
                ),
            ],
        ]

        if attempt.status == "timed_out":
            result_data.append(["Note:", "Exam was auto-submitted due to timeout"])

        result_table = Table(result_data, colWidths=[100, 350])
        result_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    # Highlight status row
                    ("TEXTCOLOR", (1, 2), (1, 2), status_color),
                    ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
                ]
            )
        )
        elements.append(result_table)
        elements.append(Spacer(1, 30))

        # Score Summary Box
        score_color = (
            colors.green
            if percentage >= 70
            else (colors.orange if percentage >= 50 else colors.red)
        )

        summary_data = [
            [f"{percentage}%", status],
        ]
        summary_table = Table(summary_data, colWidths=[225, 225])
        summary_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 24),
                    ("TEXTCOLOR", (0, 0), (0, 0), score_color),
                    ("TEXTCOLOR", (1, 0), (1, 0), status_color),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
                    ("TOPPADDING", (0, 0), (-1, -1), 20),
                    ("BOX", (0, 0), (-1, -1), 1, colors.grey),
                    ("LINEBEFORE", (1, 0), (1, 0), 1, colors.grey),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 30))

        # Footer
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
            alignment=1,  # Center
        )
        elements.append(
            Paragraph(
                "This is a computer-generated document and does not require a signature.",
                footer_style,
            )
        )
        elements.append(
            Paragraph(
                f"Generated by ExamCore on {attempt.submitted_at.strftime('%b %d, %Y') if attempt.submitted_at else 'N/A'}",
                footer_style,
            )
        )

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
