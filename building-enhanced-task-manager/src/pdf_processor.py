"""
pdf_processor.py
สร้าง PDF จากรายการงาน (task), รวมไฟล์ PDF หลายไฟล์ และใส่ลายน้ำ (watermark)
"""
import io
import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


def create_task_pdf(output_path, title, tasks):
    """สร้างไฟล์ PDF ที่มีหัวเรื่องและตารางรายการงาน"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    story = [
        Paragraph(title, styles["Title"]),
        Paragraph(f"Total tasks: {len(tasks)}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]

    rows = [["ID", "Task", "Category", "Priority", "Due Date"]]
    rows += [[t["id"], t["title"], t["category"], t["priority"], t["due_date"]] for t in tasks]
    table = Table(rows, colWidths=[1.2 * cm, 7.3 * cm, 3 * cm, 2.2 * cm, 2.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5496")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)

    doc.build(story)
    logger.info("Created PDF: %s", output_path)
    return output_path


def merge_pdfs(input_paths, output_path):
    """รวมไฟล์ PDF หลายไฟล์ตามลำดับให้เป็นไฟล์เดียว"""
    writer = PdfWriter()
    for path in input_paths:
        try:
            writer.append(str(path))
            logger.info("Appended: %s", path)
        except FileNotFoundError:
            logger.error("File not found, skipped: %s", path)

    with open(output_path, "wb") as f:
        writer.write(f)
    logger.info("Merged PDF saved: %s", output_path)
    return Path(output_path)


def _create_watermark_page(text, width, height):
    """สร้างหน้า PDF ที่มีข้อความลายน้ำเอียง 45 องศา (อยู่ในหน่วยความจำ)"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(colors.red, alpha=0.18)
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def add_watermark(input_path, output_path, text="CONFIDENTIAL"):
    """ใส่ลายน้ำลงทุกหน้าของไฟล์ PDF"""
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        page.merge_page(_create_watermark_page(text, width, height))
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)
    logger.info("Watermarked PDF saved: %s", output_path)
    return Path(output_path)
