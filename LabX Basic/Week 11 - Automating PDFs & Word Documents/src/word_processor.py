# document-automator/src/word_processor.py
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import os
from .utils import setup_logging
logger = setup_logging(__name__)
class WordProcessor:
&quot;&quot;&quot;
Handles operations related to Word documents using python-docx.
&quot;&quot;&quot;
def __init__(self):
logger.info(&quot;WordProcessor initialized.&quot;)
def create_document(self):
&quot;&quot;&quot;Creates a new blank Word document.&quot;&quot;&quot;
document = docx.Document()
logger.info(&quot;New Word document created.&quot;)
return document
def add_heading(self, document, text, level=1):
&quot;&quot;&quot;Adds a heading to the document.&quot;&quot;&quot;
document.add_heading(text, level=level)
logger.info(f&quot;Added heading (Level {level}): &#39;{text}&#39;&quot;)
def add_paragraph(self, document, text, style=None, bold=False, italic=False, font_size=None,
align=&#39;left&#39;):
&quot;&quot;&quot;Adds a paragraph with optional formatting.&quot;&quot;&quot;
paragraph = document.add_paragraph(text, style=style)
# Apply run-level formatting if specified
if paragraph.runs: # Ensure there&#39;s at least one run
run = paragraph.runs[0] # Apply to the first run

if bold:
run.bold = True
if italic:
run.italic = True
if font_size:
run.font.size = Pt(font_size)
# Apply paragraph alignment
if align == &#39;center&#39;:
paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
elif align == &#39;right&#39;:
paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
elif align == &#39;justify&#39;:
paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
else: # Default left
paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
logger.info(f&quot;Added paragraph: &#39;{text[:50]}...&#39;&quot;)
def add_table(self, document, data, include_header=True, header_bold=True, col_widths=None):
&quot;&quot;&quot;
Adds a table to the document.
`data` should be a list of lists (rows).
`col_widths` is a list of floats (in inches) for column widths.
&quot;&quot;&quot;
if not data:
logger.warning(&quot;No data provided to add table.&quot;)
return
rows = len(data)
cols = len(data[0]) if data else 0
if rows == 0 or cols == 0:
logger.warning(&quot;Table data is empty or malformed. Skipping table creation.&quot;)
return
table = document.add_table(rows=rows if include_header else rows, cols=cols) # Table will
auto-add rows later
table.style = &#39;Table Grid&#39; # Apply a basic grid style
# Set column widths if provided
if col_widths and len(col_widths) == cols:
for i, width in enumerate(col_widths):
table.columns[i].width = Inches(width)

# Populate table
for r_idx, row_data in enumerate(data):
# If header is included in data and we apply special header formatting
if include_header and r_idx == 0:
cells = table.rows[0].cells
for c_idx, cell_data in enumerate(row_data):
cells[c_idx].text = str(cell_data)
if header_bold:
cells[c_idx].paragraphs[0].runs[0].bold = True
else:
row_obj = table.rows[r_idx]
for c_idx, cell_data in enumerate(row_data):
row_obj.cells[c_idx].text = str(cell_data)
logger.info(f&quot;Added table with {rows} rows and {cols} columns.&quot;)
def add_picture(self, document, image_path, width_inches=None):
&quot;&quot;&quot;Adds an image to the document with optional width scaling.&quot;&quot;&quot;
if not os.path.exists(image_path):
logger.error(f&quot;Image file not found: {image_path}&quot;)
return False
try:
if width_inches:
document.add_picture(image_path, width=Inches(width_inches))
else:
document.add_picture(image_path)
logger.info(f&quot;Added picture: {os.path.basename(image_path)}&quot;)
return True
except Exception as e:
logger.error(f&quot;Error adding picture &#39;{image_path}&#39;: {e}&quot;)
return False
def save_document(self, document, output_path):
&quot;&quot;&quot;Saves the Word document to a specified path.&quot;&quot;&quot;
try:
document.save(output_path)
logger.info(f&quot;Word document saved to &#39;{output_path}&#39;.&quot;)
return True
except Exception as e:
logger.error(f&quot;Error saving Word document to &#39;{output_path}&#39;: {e}&quot;)
return False