"""
main.py
เวิร์กโฟลว์หลักของ Enhanced Task Manager:
  1. อ่านรายการงานจาก data/tasks.json
  2. สร้าง PDF แยกตามสถานะงาน แล้วรวมเป็น output/merged_docs.pdf
  3. สร้างรายงาน Word output/generate_report.docx
  4. ใส่ลายน้ำให้ PDF ที่รวมแล้ว -> output/watermarked_document.pdf

วิธีรัน (จากโฟลเดอร์ Week11):  python src/main.py
"""
import json
import logging
from pathlib import Path

from docx_generator import generate_report
from pdf_processor import add_watermark, create_task_pdf, merge_pdfs

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "tasks.json"
OUTPUT_DIR = BASE_DIR / "output"
PARTS_DIR = OUTPUT_DIR / "parts"

STATUSES = ["Done", "In Progress", "To Do"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_tasks(path):
    """อ่านรายการงานจากไฟล์ JSON"""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Task file not found: %s", path)
        return []
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", path, e)
        return []


def main():
    tasks = load_tasks(DATA_FILE)
    if not tasks:
        logger.error("No tasks to process. Exiting.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1) สร้าง PDF แยกตามสถานะ แล้วรวมเป็นไฟล์เดียว
    part_files = []
    for status in STATUSES:
        group = [t for t in tasks if t["status"] == status]
        if group:
            filename = PARTS_DIR / f"tasks_{status.lower().replace(' ', '_')}.pdf"
            part_files.append(create_task_pdf(filename, f"Tasks - {status}", group))

    merged = merge_pdfs(part_files, OUTPUT_DIR / "merged_docs.pdf")

    # 2) สร้างรายงาน Word
    generate_report(tasks, OUTPUT_DIR / "generate_report.docx")

    # 3) ใส่ลายน้ำให้ PDF ที่รวมแล้ว
    add_watermark(merged, OUTPUT_DIR / "watermarked_document.pdf", text="CONFIDENTIAL")

    logger.info("All done! Output files are in: %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
