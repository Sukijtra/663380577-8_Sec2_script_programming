# spreadsheet-automator/main.py
import sys
import os
# Add the &#39;src&#39; directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), &#39;src&#39;))
from excel_processor import ExcelProcessor
def main():
&quot;&quot;&quot;
Main entry point for the spreadsheet automation application.
&quot;&quot;&quot;
input_file = os.path.join(&#39;data&#39;, &#39;input_sales.xlsx&#39;)
output_file = os.path.join(&#39;data&#39;, &#39;output_sales_report.xlsx&#39;)
# Ensure the &#39;data&#39; directory exists
os.makedirs(&#39;data&#39;, exist_ok=True)
# Check if the input file exists as it&#39;s required for the prototype
if not os.path.exists(input_file):
print(f&quot;Error: Input file &#39;{input_file}&#39; not found.&quot;)
print(&quot;Please create &#39;input_sales.xlsx&#39; in the &#39;data&#39; folder with sample sales data (Product Name,
Quantity, Unit Price).&quot;)
print(&quot;Refer to the README.md for example content.&quot;)

return
processor = ExcelProcessor()
print(f&quot;Starting sales data processing from &#39;{input_file}&#39;...&quot;)
success = processor.process_sales_data(input_file, output_file)
if success:
print(f&quot;Sales report successfully generated and saved to &#39;{output_file}&#39;.&quot;)
else:
print(&quot;Failed to generate sales report.&quot;)
if __name__ == &quot;__main__&quot;:
main()