from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph, Spacer, Table, TableStyle

from apps.legal.models import LegalDocument


SECTION_RE = re.compile(r"^(?P<number>\d+\.?)(\s+)(?P<title>[A-Z][^\n]{2,})$")
SUBSECTION_RE = re.compile(r"^(?P<number>\d+\.\d+)(\s+)(?P<text>.+)$")
SIGNATURE_RE = re.compile(
    r"^(For |Accepted by|Accepted and agreed by|Candidate Acceptance|Execution|Signature:|Name:|Title:|Designation:|Date:|Authorized Signatory|Employee Signature|Candidate Signature|Intern Signature|Partner Signature|Freelancer Signature)",
    re.IGNORECASE,
)
SCHEDULE_RE = re.compile(r"^(Schedule|Annexure)\s+\d+", re.IGNORECASE)
LABEL_RE = re.compile(r"^(?P<label>[A-Za-z][A-Za-z /.-]{1,42}:)(?P<value>.*)$")
SIGNATURE_LABEL_RE = re.compile(r"^(Name|Title|Designation|Date):(?P<value>.*)$", re.IGNORECASE)

PAGE_WIDTH, PAGE_HEIGHT = LETTER
BODY_TEXT_COLOR = colors.HexColor("#1f2937")
BORDER_COLOR = colors.HexColor("#d8e0ea")
MUTED_RULE_COLOR = colors.HexColor("#e6ebf1")


class PDFService:
    @staticmethod
    def render_document(document: LegalDocument) -> bytes:
        buffer = BytesIO()
        content = document.content.strip()
        display_title, content = PDFService._extract_display_title(document.title, content)
        branding = document.branding or {}
        template = document.template
        scheme = (template.color_scheme if template else {}) or {}
        primary = colors.HexColor(scheme.get("primary", "#0f172a"))
        accent = colors.HexColor(scheme.get("accent", "#0f766e"))
        secondary = colors.HexColor(scheme.get("secondary", "#475569"))
        font = template.font if template and template.font else "Helvetica"
        font_set = PDFService._font_set(font)

        doc = BaseDocTemplate(
            buffer,
            pagesize=LETTER,
            leftMargin=0.62 * inch,
            rightMargin=0.62 * inch,
            topMargin=1.36 * inch,
            bottomMargin=0.78 * inch,
            title=display_title,
        )
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
        doc.addPageTemplates(
            [
                PageTemplate(
                    id="branded",
                    frames=[frame],
                    onPage=lambda canvas, pdf_doc: PDFService._draw_page(
                        canvas, pdf_doc, document, branding, primary, accent, secondary, font_set
                    ),
                )
            ]
        )

        styles = PDFService._styles(font_set, primary, secondary)
        story = [Paragraph(PDFService._escape(display_title), styles["DocumentTitle"]), Spacer(1, 8)]
        story.extend(PDFService._content_flowables(content, styles, primary, accent))

        doc.build(story)
        return buffer.getvalue()

    @staticmethod
    def _font_set(font: str) -> dict[str, str]:
        if font.startswith("Times"):
            return {"regular": "Times-Roman", "bold": "Times-Bold", "italic": "Times-Italic"}
        return {"regular": "Helvetica", "bold": "Helvetica-Bold", "italic": "Helvetica-Oblique"}

    @staticmethod
    def _styles(font_set: dict[str, str], primary, secondary):
        base = getSampleStyleSheet()
        return {
            "DocumentTitle": ParagraphStyle(
                "DocumentTitle",
                parent=base["Title"],
                fontName=font_set["bold"],
                fontSize=18.5,
                leading=23,
                textColor=primary,
                alignment=TA_CENTER,
                spaceAfter=13,
            ),
            "Section": ParagraphStyle(
                "Section",
                parent=base["Heading2"],
                fontName=font_set["bold"],
                fontSize=11.4,
                leading=15,
                textColor=primary,
                spaceBefore=13,
                spaceAfter=5.5,
                keepWithNext=True,
            ),
            "Clause": ParagraphStyle(
                "Clause",
                parent=base["BodyText"],
                fontName=font_set["regular"],
                fontSize=10.1,
                leading=15.8,
                textColor=BODY_TEXT_COLOR,
                leftIndent=20,
                firstLineIndent=-20,
                spaceAfter=6.2,
            ),
            "Body": ParagraphStyle(
                "Body",
                parent=base["BodyText"],
                fontName=font_set["regular"],
                fontSize=10.1,
                leading=15.8,
                textColor=BODY_TEXT_COLOR,
                alignment=TA_LEFT,
                spaceAfter=7.2,
            ),
            "BodyLabel": ParagraphStyle(
                "BodyLabel",
                parent=base["BodyText"],
                fontName=font_set["regular"],
                fontSize=10.1,
                leading=15.8,
                textColor=BODY_TEXT_COLOR,
                spaceAfter=5.4,
            ),
            "Signature": ParagraphStyle(
                "Signature",
                parent=base["BodyText"],
                fontName=font_set["regular"],
                fontSize=10,
                leading=15.5,
                textColor=BODY_TEXT_COLOR,
                spaceBefore=2,
                spaceAfter=2.5,
            ),
            "SignatureLine": ParagraphStyle(
                "SignatureLine",
                parent=base["BodyText"],
                fontName=font_set["regular"],
                fontSize=10.5,
                leading=16,
                textColor=BODY_TEXT_COLOR,
                spaceBefore=13,
                spaceAfter=1,
            ),
            "Small": ParagraphStyle(
                "Small",
                parent=base["BodyText"],
                fontName=font_set["regular"],
                fontSize=8.2,
                leading=11,
                textColor=secondary,
            ),
            "SmallLabel": ParagraphStyle(
                "SmallLabel",
                parent=base["BodyText"],
                fontName=font_set["bold"],
                fontSize=8.2,
                leading=11,
                textColor=secondary,
            ),
        }

    @staticmethod
    def _content_flowables(content: str, styles, primary, accent):
        flowables = []
        for block in content.split("\n\n"):
            text = block.strip()
            if not text:
                continue

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if len(lines) > 2 and all(":" in line for line in lines) and not any(SIGNATURE_RE.match(line) for line in lines):
                rows = []
                for line in lines:
                    key, value = line.split(":", 1)
                    rows.append(
                        [
                            Paragraph(PDFService._escape(key.upper()), styles["SmallLabel"]),
                            Paragraph(PDFService._escape(value.strip()), styles["Body"]),
                        ]
                    )
                table = Table(rows, colWidths=[1.75 * inch, 4.95 * inch], hAlign="LEFT")
                table.setStyle(
                    TableStyle(
                        [
                            ("LINEBELOW", (0, 0), (-1, -1), 0.25, MUTED_RULE_COLOR),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                flowables.extend([table, Spacer(1, 9)])
                continue

            if any(SIGNATURE_RE.match(line) or "________________" in line for line in lines):
                flowables.append(KeepTogether(PDFService._signature_flowables(lines, styles)))
                continue

            for line in lines:
                section = SECTION_RE.match(line)
                subsection = SUBSECTION_RE.match(line)
                if section or SCHEDULE_RE.match(line) or line.isupper():
                    flowables.append(Paragraph(PDFService._escape(line), styles["Section"]))
                    continue
                if subsection:
                    number = subsection.group("number")
                    body = subsection.group("text")
                    flowables.append(Paragraph(f"<b>{PDFService._escape(number)}</b> {PDFService._escape(body)}", styles["Clause"]))
                    continue
                label = LABEL_RE.match(line)
                if label and len(label.group("value").strip()) < 140:
                    flowables.append(
                        Paragraph(
                            f"<b>{PDFService._escape(label.group('label'))}</b>{PDFService._escape(label.group('value'))}",
                            styles["BodyLabel"],
                        )
                    )
                    continue
                flowables.append(Paragraph(PDFService._escape(line), styles["Body"]))

        return flowables

    @staticmethod
    def _signature_flowables(lines: list[str], styles):
        flowables = [Spacer(1, 8)]
        for line in lines:
            if not line:
                continue
            if line.lower() == "execution":
                flowables.extend([Spacer(1, 4), Paragraph(PDFService._escape(line), styles["Section"])])
                continue
            if "________________" in line:
                flowables.append(Paragraph("____________________________", styles["SignatureLine"]))
                continue
            label = SIGNATURE_LABEL_RE.match(line)
            if label:
                value = label.group("value")
                flowables.append(
                    Paragraph(f"<b>{PDFService._escape(label.group(1) + ':')}</b>{PDFService._escape(value)}", styles["Signature"])
                )
                continue
            flowables.append(Paragraph(PDFService._escape(line), styles["Signature"]))
        flowables.append(Spacer(1, 8))
        return flowables

    @staticmethod
    def _draw_page(canvas, doc, document: LegalDocument, branding: dict, primary, accent, secondary, font_set):
        width, height = PAGE_WIDTH, PAGE_HEIGHT
        left = doc.leftMargin
        right = width - doc.rightMargin
        top = height - 0.34 * inch

        company_name = branding.get("company_name") or branding.get("name") or ""
        address = branding.get("address") or ""
        contact = " | ".join(
            item
            for item in [
                branding.get("phone"),
                branding.get("email"),
                branding.get("website"),
                branding.get("registration_number"),
                branding.get("gst_number"),
            ]
            if item
        )

        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#fcfdff"))
        canvas.rect(0, height - 1.08 * inch, width, 1.08 * inch, stroke=0, fill=1)
        canvas.setStrokeColor(BORDER_COLOR)
        canvas.setLineWidth(0.5)
        canvas.line(left, height - 1.08 * inch, right, height - 1.08 * inch)
        canvas.setStrokeColor(accent)
        canvas.setLineWidth(2.2)
        canvas.line(left, height - 1.08 * inch, left + 1.6 * inch, height - 1.08 * inch)

        logo_drawn = False
        logo_right = left
        if document.company_logo:
            logo_path = Path(document.company_logo.path)
            if logo_path.exists():
                try:
                    image = ImageReader(str(logo_path))
                    image_width, image_height = image.getSize()
                    max_width = 2.45 * inch
                    max_height = 0.84 * inch
                    scale = min(max_width / image_width, max_height / image_height)
                    draw_width = image_width * scale
                    draw_height = image_height * scale
                    logo_y = height - 0.3 * inch - draw_height
                    canvas.drawImage(
                        image,
                        left,
                        logo_y,
                        width=draw_width,
                        height=draw_height,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                    logo_right = left + draw_width
                    logo_drawn = True
                except Exception:
                    logo_drawn = False

        text_left = max(left + 2.2 * inch, logo_right + 0.34 * inch) if logo_drawn else left
        canvas.setFillColor(primary)
        canvas.setFont(font_set["bold"], 13)
        canvas.drawString(text_left, top, company_name or "Professional Document")
        canvas.setFillColor(secondary)
        canvas.setFont(font_set["regular"], 8.1)
        if address:
            canvas.drawString(text_left, top - 0.2 * inch, address[:105])
        if contact:
            canvas.drawString(text_left, top - 0.38 * inch, contact[:110])

        canvas.setFillColor(secondary)
        canvas.setFont(font_set["regular"], 7.7)
        footer_y = 0.42 * inch
        canvas.drawRightString(right, footer_y, f"Page {doc.page}")
        canvas.drawString(left, footer_y, (company_name or document.title)[:82])
        canvas.setStrokeColor(MUTED_RULE_COLOR)
        canvas.setLineWidth(0.5)
        canvas.line(left, 0.64 * inch, right, 0.64 * inch)
        canvas.restoreState()

    @staticmethod
    def _extract_display_title(fallback: str, content: str) -> tuple[str, str]:
        if not content:
            return fallback, content

        blocks = content.split("\n\n")
        first_block = blocks[0].strip()
        first_lines = [line.strip() for line in first_block.splitlines() if line.strip()]
        if len(first_lines) == 1:
            first_line = first_lines[0]
            is_document_title = (
                first_line.isupper()
                and len(first_line) <= 90
                and ":" not in first_line
                and not first_line[0].isdigit()
            )
            if is_document_title:
                return first_line.title(), "\n\n".join(blocks[1:]).strip()

        return fallback, content

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\u2013", "-")
            .replace("\u2014", "-")
        )
