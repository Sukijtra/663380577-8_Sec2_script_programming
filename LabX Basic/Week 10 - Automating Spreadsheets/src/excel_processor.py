# spreadsheet-automator/src/excel_processor.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
class ExcelProcessor:
&quot;&quot;&quot;
A class to encapsulate common Excel processing functionalities using openpyxl.
&quot;&quot;&quot;
def __init__(self):
pass
def create_workbook(self, filename=&quot;new_workbook.xlsx&quot;):
&quot;&quot;&quot;Creates a new Excel workbook.&quot;&quot;&quot;
wb = openpyxl.Workbook()
# Remove default sheet
if &#39;Sheet&#39; in wb.sheetnames:
del wb[&#39;Sheet&#39;]
print(f&quot;New workbook &#39;{filename}&#39; created.&quot;)
return wb
def load_workbook(self, filename):
&quot;&quot;&quot;Loads an existing Excel workbook.&quot;&quot;&quot;
try:
wb = openpyxl.load_workbook(filename)

print(f&quot;Workbook &#39;{filename}&#39; loaded successfully.&quot;)
return wb
except FileNotFoundError:
print(f&quot;Error: Workbook &#39;{filename}&#39; not found.&quot;)
return None
except Exception as e:
print(f&quot;Error loading workbook &#39;{filename}&#39;: {e}&quot;)
return None
def save_workbook(self, workbook, filename):
&quot;&quot;&quot;Saves a workbook to a specified filename.&quot;&quot;&quot;
try:
workbook.save(filename)
print(f&quot;Workbook saved to &#39;{filename}&#39;.&quot;)
return True
except Exception as e:
print(f&quot;Error saving workbook to &#39;{filename}&#39;: {e}&quot;)
return False
def process_sales_data(self, input_filename, output_filename):
&quot;&quot;&quot;
Loads sales data, calculates totals, and writes to a new formatted Excel file.
Assumes input columns: Product Name, Quantity, Unit Price.
&quot;&quot;&quot;
input_wb = self.load_workbook(input_filename)
if not input_wb:
return False
input_sheet = input_wb.active # Assumes data is in the active sheet
# Create a new workbook for output
output_wb = self.create_workbook()
output_sheet = output_wb.create_sheet(&quot;Sales Report&quot;, 0)
# Define styles
header_font = Font(bold=True, color=&quot;FFFFFF&quot;)
header_fill = PatternFill(start_color=&quot;4CAF50&quot;, end_color=&quot;4CAF50&quot;, fill_type=&quot;solid&quot;) # Green
total_row_font = Font(bold=True, color=&quot;000000&quot;)
total_row_fill = PatternFill(start_color=&quot;FFEB3B&quot;, end_color=&quot;FFEB3B&quot;, fill_type=&quot;solid&quot;) #
Yellow
thin_border = Border(left=Side(style=&#39;thin&#39;), right=Side(style=&#39;thin&#39;), top=Side(style=&#39;thin&#39;),
bottom=Side(style=&#39;thin&#39;))
currency_format = &#39;#,##0.00&#39; # Standard currency format
# Write headers to output sheet

headers = [&quot;Product Name&quot;, &quot;Quantity&quot;, &quot;Unit Price&quot;, &quot;Total Price&quot;]
for col_num, header in enumerate(headers, 1):
cell = output_sheet.cell(row=1, column=col_num, value=header)
cell.font = header_font
cell.fill = header_fill
cell.border = thin_border
cell.alignment = Alignment(horizontal=&#39;center&#39;, vertical=&#39;center&#39;)
grand_total = 0
output_row = 2 # Start writing data from row 2
# Iterate through rows in input sheet, skipping header
for row_index, row in enumerate(input_sheet.iter_rows(min_row=2, values_only=True), 2):
if not any(row): # Skip empty rows
continue
product_name = row[0] if len(row) &gt; 0 else None
quantity = row[1] if len(row) &gt; 1 else 0
unit_price = row[2] if len(row) &gt; 2 else 0.0
# Basic type conversion and error handling
try:
quantity = int(quantity)
unit_price = float(unit_price)
except (ValueError, TypeError):
print(f&quot;Warning: Skipping row {row_index} due to invalid number format: {row}&quot;)
continue
total_price = quantity * unit_price
grand_total += total_price
# Write data to output sheet
output_sheet.cell(row=output_row, column=1, value=product_name).border =
thin_border
output_sheet.cell(row=output_row, column=2, value=quantity).border = thin_border
output_sheet.cell(row=output_row, column=3, value=unit_price).border = thin_border
total_price_cell = output_sheet.cell(row=output_row, column=4, value=total_price)
total_price_cell.number_format = currency_format
total_price_cell.border = thin_border
output_row += 1
# Write grand total
output_sheet.merge_cells(start_row=output_row, start_column=1, end_row=output_row,

end_column=3)
grand_total_label_cell = output_sheet.cell(row=output_row, column=1, value=&quot;Grand
Total:&quot;)
grand_total_label_cell.font = total_row_font
grand_total_label_cell.fill = total_row_fill
grand_total_label_cell.alignment = Alignment(horizontal=&#39;right&#39;, vertical=&#39;center&#39;) # Align label
right
grand_total_value_cell = output_sheet.cell(row=output_row, column=4, value=grand_total)
grand_total_value_cell.font = total_row_font
grand_total_value_cell.fill = total_row_fill
grand_total_value_cell.number_format = currency_format
grand_total_value_cell.border = thin_border
# Adjust column widths for better readability
for col_num in range(1, len(headers) + 1):
max_length = 0
column_letter = get_column_letter(col_num)
for cell in output_sheet[column_letter]:
try:
if cell.value:
max_length = max(max_length, len(str(cell.value)))
except:
pass
adjusted_width = (max_length + 2) # Add a little padding
if adjusted_width &gt; 0: # Avoid setting zero width
output_sheet.column_dimensions[column_letter].width = adjusted_width
return self.save_workbook(output_wb, output_filename)