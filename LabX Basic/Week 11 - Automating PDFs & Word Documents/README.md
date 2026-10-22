# Week 17: Automating PDFs &amp; Word Documents
This project demonstrates how to automate common tasks involving PDF and Word documents
using Python. It leverages `PyPDF2` for PDF manipulation and `python-docx` for Word document
creation and modification.
## Key Concepts Demonstrated

* **PDF Text Extraction**: Reading text content from PDF files.
* **PDF Merging**: Combining multiple PDF files into a single document.
* **Word Document Creation**: Programmatically generating new `.docx` files.
* **Adding Content to Word**: Inserting headings, paragraphs, formatted text (bold, italic, font
size), and tables.
* **Modular Design**: Separating PDF and Word processing logic into distinct modules
(`pdf_processor.py`, `word_processor.py`).
* **Robustness**: Basic error handling for file operations and library interactions, with logging for
workflow visibility.
## Setup &amp; How to Run
1. **Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/document-
automator.git](https://github.com/YOUR_USERNAME/document-automator.git)
cd document-automator
```
2. **Install Dependencies:**
It&#39;s highly recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate.bat
pip install PyPDF2 python-docx
```
3. **Prepare Input Documents:**
* Create a folder named `documents` in the root of your project: `mkdir documents`.
* **`input_article.pdf`**: Place a sample PDF file with some text content in the `documents` folder. This
PDF&#39;s text will be extracted and inserted into the Word document.
* **`dummy_doc1.pdf` &amp; `dummy_doc2.pdf`**: For the PDF merging example, create two very small,
simple PDF files (e.g., just one line of text) and place them in the `documents` folder.
**Example Content Idea for `input_article.pdf` (Save as PDF):**
```
Introduction to Automation
Automation is the creation and application of technology to produce and deliver goods and services
with minimal human intervention. The implementation of automation technologies, techniques, and
processes improves the efficiency, reliability, and speed of many tasks that were previously performed
manually. This leads to increased productivity, reduced costs, and improved quality.
Benefits of Automation
1. Increased Efficiency: Tasks are completed faster and with higher throughput.
2. Cost Reduction: Lower labor costs and reduced waste.
3. Improved Accuracy: Minimizes human error.
4. Enhanced Safety: Dangerous tasks can be automated.

5. Greater Consistency: Uniform quality in output.
Conclusion
Automation is transforming industries globally. Embracing these technologies is crucial for future
competitiveness.
```
4. **Run the script:**
```bash
python main.py
```
The script will:
* Extract text from `input_article.pdf`.
* Create `output_report.docx` in the `documents` folder, containing the extracted text, a custom
heading, and a summary table.
* If `dummy_doc1.pdf` and `dummy_doc2.pdf` are present, it will merge them into `merged_output.pdf`.
## Project Structure

document-automator/
├── src/
│ ├── init.py # Python package marker
│ ├── pdf_processor.py # Logic for PyPDF2 operations (extract, merge, split)
│ ├── word_processor.py # Logic for python-docx operations (create, add content, format)
│ └── utils.py # General utilities (logging, directory creation)
├── documents/
│ ├── input_article.pdf # Sample PDF for text extraction (YOU CREATE THIS)
│ ├── dummy_doc1.pdf # Sample PDF for merging (YOU CREATE THIS)
│ ├── dummy_doc2.pdf # Sample PDF for merging (YOU CREATE THIS)
│ └── output_report.docx # Generated Word document
│ └── merged_output.pdf # Generated merged PDF (if merge task runs)
├── main.py # Application entry point to orchestrate tasks
├── .gitignore # Files/folders to ignore in Git
└── README.md # This project overview

## Debugging Document Automation
* **`FileNotFoundError`**: Ensure your input PDF files (`input_article.pdf`, `dummy_doc1.pdf`,
`dummy_doc2.pdf`) are correctly placed in the `documents` directory and their names match
exactly in `main.py`.
* **`PyPDF2.errors.PdfReadError`**: This often means the PDF file is corrupted, encrypted with
an unknown password, or not a valid PDF. Ensure your input PDFs are standard and readable.

* **Blank Word Document / Missing Content**:
* Check if `pdf_processor.extract_text_from_pdf()` actually returned text. If it&#39;s `None` or
empty, the Word document will be empty. Some PDFs are image-based and don&#39;t contain
selectable text.
* Verify that `add_paragraph`, `add_heading`, `add_table` calls are correctly made *before*
`save_document`.
* **Formatting Issues in Word**: `python-docx` sometimes requires specific sequences for
complex formatting.
* For runs within paragraphs, ensure you&#39;re accessing `paragraph.runs[0]` or iterating through
runs if you add text in parts.
* Font sizes are in points (`Pt()`).
* **Logging Output**: The `logging` module provides detailed messages in the console. Pay
attention to `ERROR` and `WARNING` messages to pinpoint issues.
## Extension Ideas (Future Work)
* **Template-Based Document Generation**: Create a Word template (`.docx`) with
placeholders (e.g., `{{name}}`, `{{date}}`) and use `python-docx` to find and replace these
placeholders with data from a source (e.g., Excel, CSV, database). This is powerful for
generating many similar documents.
* **Advanced PDF Parsing**: For complex PDFs with varying layouts, consider libraries like
`pdfminer.six` or `PyMuPDF` (Fitz) which offer more control over text extraction and layout
analysis.
* **PDF to Image/Image to PDF**: Convert PDF pages to images or assemble images into a
PDF.
* **Document Conversions**: Explore libraries or external tools (like Pandoc) for converting
between Word, PDF, HTML, etc.
* **Mail Merge Automation**: Combine spreadsheet data with a Word template to generate
personalized documents (e.g., letters, certificates).
* **Web-to-PDF/Word**: Integrate with web scraping to extract data and then generate a
structured report in PDF or Word.
* **Document Comparison**: Use Python to compare two versions of a document (textually).
* **Document Search/Indexing**: Build a script to index text content from a directory of
documents for quick searching.