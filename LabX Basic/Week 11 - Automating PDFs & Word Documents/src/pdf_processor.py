# document-automator/src/pdf_processor.py
from PyPDF2 import PdfReader, PdfWriter
import os
from .utils import setup_logging
logger = setup_logging(__name__)
class PDFProcessor:
&quot;&quot;&quot;
Handles operations related to PDF files using PyPDF2.
&quot;&quot;&quot;
def __init__(self):
logger.info(&quot;PDFProcessor initialized.&quot;)
def extract_text_from_pdf(self, pdf_path):
&quot;&quot;&quot;
Extracts all text from a given PDF file.
&quot;&quot;&quot;
if not os.path.exists(pdf_path):

logger.error(f&quot;PDF file not found: {pdf_path}&quot;)
return None
text_content = &quot;&quot;
try:
reader = PdfReader(pdf_path)
num_pages = len(reader.pages)
logger.info(f&quot;Extracting text from &#39;{pdf_path}&#39; ({num_pages} pages)...&quot;)
for page_num in range(num_pages):
page = reader.pages[page_num]
text_content += page.extract_text() + &quot;\n--- Page End ---\n&quot; # Separator for readability
logger.info(f&quot;Successfully extracted text from &#39;{pdf_path}&#39;.&quot;)
return text_content
except Exception as e:
logger.error(f&quot;Error extracting text from &#39;{pdf_path}&#39;: {e}&quot;)
return None
def merge_pdfs(self, pdf_paths, output_path):
&quot;&quot;&quot;
Merges multiple PDF files into a single output PDF.
&quot;&quot;&quot;
if not pdf_paths:
logger.warning(&quot;No PDF paths provided for merging.&quot;)
return False
writer = PdfWriter()
logger.info(f&quot;Merging PDFs into &#39;{output_path}&#39;...&quot;)
for pdf_path in pdf_paths:
if not os.path.exists(pdf_path):
logger.warning(f&quot;Skipping non-existent PDF for merging: {pdf_path}&quot;)
continue
try:
reader = PdfReader(pdf_path)
for page in reader.pages:
writer.add_page(page)
logger.info(f&quot;Added &#39;{pdf_path}&#39; to merge queue.&quot;)
except Exception as e:
logger.error(f&quot;Error reading PDF &#39;{pdf_path}&#39; for merging: {e}&quot;)
continue
if len(writer.pages) == 0:
logger.warning(&quot;No pages were added to the merged PDF. Output file will be empty or not
created.&quot;)

return False
try:
with open(output_path, &#39;wb&#39;) as f:
writer.write(f)
logger.info(f&quot;PDFs successfully merged to &#39;{output_path}&#39;.&quot;)
return True
except Exception as e:
logger.error(f&quot;Error writing merged PDF to &#39;{output_path}&#39;: {e}&quot;)
return False
def split_pdf(self, pdf_path, output_dir=&quot;.&quot;, pages_per_split=1):
&quot;&quot;&quot;
Splits a PDF into multiple smaller PDFs, each containing a specified number of pages.
&quot;&quot;&quot;
if not os.path.exists(pdf_path):
logger.error(f&quot;PDF file not found: {pdf_path}&quot;)
return False
ensure_directory_exists(output_dir)
try:
reader = PdfReader(pdf_path)
total_pages = len(reader.pages)
logger.info(f&quot;Splitting &#39;{pdf_path}&#39; ({total_pages} pages) into chunks of {pages_per_split}
pages.&quot;)
for i in range(0_int, total_pages, pages_per_split):
writer = PdfWriter()
output_filename = os.path.join(output_dir,
f&quot;{os.path.splitext(os.path.basename(pdf_path))[0]}_part_{(i // pages_per_split) + 1}.pdf&quot;)
for j in range(i, min(i + pages_per_split, total_pages)):
writer.add_page(reader.pages[j])
with open(output_filename, &#39;wb&#39;) as f:
writer.write(f)
logger.info(f&quot;Created split PDF: {output_filename}&quot;)
logger.info(f&quot;Successfully split &#39;{pdf_path}&#39;.&quot;)
return True
except Exception as e:
logger.error(f&quot;Error splitting PDF &#39;{pdf_path}&#39;: {e}&quot;)
return False