# document-automator/main.py
import sys
import os
# Add the &#39;src&#39; directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from pdf_processor import PDFProcessor
from word_processor import WordProcessor
from utils import ensure_directory_exists, setup_logging
logger = setup_logging(__name__)
def main():
&quot;&quot;&quot;
Main entry point for the document automation application.
&quot;&quot;&quot;
documents_dir = os.path.join(os.path.dirname(__file__), &#39;documents&#39;)
ensure_directory_exists(documents_dir)
# --- Configuration for Input/Output Files ---
input_pdf_path = os.path.join(documents_dir, &#39;input_article.pdf&#39;)
output_docx_path = os.path.join(documents_dir, &#39;output_report.docx&#39;)
merged_pdf_output_path = os.path.join(documents_dir, &#39;merged_output.pdf&#39;)
dummy_pdf1 = os.path.join(documents_dir, &#39;dummy_doc1.pdf&#39;)
dummy_pdf2 = os.path.join(documents_dir, &#39;dummy_doc2.pdf&#39;)
# Check if essential input PDF exists
if not os.path.exists(input_pdf_path):
logger.critical(f&quot;Required input PDF &#39;{input_pdf_path}&#39; not found.&quot;)
logger.info(&quot;Please create this PDF in the &#39;documents&#39; folder with some text content.&quot;)
return
# Check for dummy PDFs for merging example
dummy_pdfs_exist = os.path.exists(dummy_pdf1) and os.path.exists(dummy_pdf2)
if not dummy_pdfs_exist:
logger.warning(&quot;Dummy PDFs for merging example (dummy_doc1.pdf, dummy_doc2.pdf) not
found. Skipping PDF merge task.&quot;)
pdf_proc = PDFProcessor()
word_proc = WordProcessor()
logger.info(&quot;--- Starting Document Automation Workflow ---&quot;)
# --- Task 1: Extract Text from PDF and Create Word Report ---

logger.info(&quot;\nTask 1: Extracting text from PDF and generating Word report.&quot;)
extracted_text = pdf_proc.extract_text_from_pdf(input_pdf_path)
if extracted_text:
doc = word_proc.create_document()
word_proc.add_heading(doc, &quot;Automated Document Report&quot;, level=1)
word_proc.add_paragraph(doc, &quot;This report was automatically generated from PDF content and
structured data.&quot;, bold=True, font_size=12)
word_proc.add_paragraph(doc, &quot;--- Extracted Content from PDF ---&quot;, italic=True, font_size=10,
align=&#39;center&#39;)
word_proc.add_paragraph(doc, extracted_text) # Add the extracted text
word_proc.add_heading(doc, &quot;Summary Data&quot;, level=2)
# Example data for a table
table_data = [
[&quot;Metric&quot;, &quot;Value&quot;, &quot;Notes&quot;],
[&quot;Total Pages Processed&quot;, str(extracted_text.count(&quot;--- Page End ---&quot;)), &quot;From Input PDF&quot;],
[&quot;Document Type&quot;, &quot;PDF/Word Hybrid&quot;, &quot;&quot;],
[&quot;Generated Date&quot;, datetime.date.today().isoformat(), &quot;&quot;]
]
word_proc.add_table(doc, table_data, col_widths=[1.5, 1.5, 3.0]) # Example column widths
word_proc.save_document(doc, output_docx_path)
else:
logger.error(&quot;Could not extract text from PDF. Skipping Word document generation.&quot;)
# --- Task 2: Merge Multiple PDFs (Optional Example) ---
if dummy_pdfs_exist:
logger.info(&quot;\nTask 2: Merging dummy PDFs.&quot;)
pdfs_to_merge = [dummy_pdf1, dummy_pdf2]
pdf_proc.merge_pdfs(pdfs_to_merge, merged_pdf_output_path)
else:
logger.warning(&quot;\nSkipping PDF merge task as dummy PDFs (dummy_doc1.pdf,
dummy_doc2.pdf) were not found.&quot;)
logger.info(&quot;--- Document Automation Workflow Completed ---&quot;)
if __name__ == &quot;__main__&quot;:
import datetime # Import inside main or globally, depending on preference
main()