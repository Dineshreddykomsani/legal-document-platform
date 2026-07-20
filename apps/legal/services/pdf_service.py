from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from apps.legal.models import LegalDocument


class PDFService:
    @staticmethod
    def render_document(document: LegalDocument) -> bytes:
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48)
        styles = getSampleStyleSheet()
        story = [Paragraph(document.title, styles["Title"]), Spacer(1, 18)]
        for block in document.content.split("\n\n"):
            if block.strip():
                story.append(Paragraph(block.replace("\n", "<br/>"), styles["BodyText"]))
                story.append(Spacer(1, 10))
        pdf.build(story)
        return buffer.getvalue()
