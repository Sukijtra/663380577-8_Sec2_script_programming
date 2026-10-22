# Week 10: Advanced Spreadsheet Automation & Agentic Workflows

This project implements an "Agentic Spreadsheet Processor" that performs a series of tasks on Excel `.xlsx` files based on a declarative JSON configuration. It showcases advanced `openpyxl` features — charts, conditional formatting, formulas, data validation and sheet protection — inside a task-driven automation framework with an audit log.

## Key Concepts Demonstrated

* **`openpyxl` Advanced Features**
    * **Charts**: Bar, Line and Pie charts (`BarChart`, `LineChart`, `PieChart`, `Reference`), including data from another sheet (`'Raw Data'!D1:D10`).
    * **Conditional Formatting**: `ColorScaleRule`, `DataBarRule`, `IconSetRule` and formula-based rules (`FormulaRule`).
    * **Formulas**: Writing row-by-row formulas (`=B{row}*C{row}`) and summary formulas (`SUM`, `AVERAGE`, `MAX`, `COUNTIF`).
    * **Data Validation**: Dropdown lists and number/date/text-length rules (`DataValidation`).
    * **Sheet Protection**: Locking a sheet so formulas cannot be changed by accident.
* **Agentic Design with Configuration**: `configs/example_spreadsheet_config.json` is the agent's "plan". The agent reads each task, and a **task dispatcher** calls the matching handler.
* **Robustness**: Every task runs inside its own `try/except`, so one failing task does not stop the workflow.
* **Audit Logging**: An **"Audit Log"** sheet is added to the output workbook with the time, status (colored), task type and message of every step.
* **Google Sheets (optional)**: `google_sheets_utils.py` can upload the processed sheets with `gspread` when enabled in the config.

## Setup & How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
    cd 663380577-8_Sec2_script_programming/agentic-spreadsheet-processor
    ```
2. **Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
    pip install -r requirements.txt
    ```
3. **Input data** is provided in `data/input_data.xlsx` (sheet **`SalesData`**):

    | Product Name | Quantity | Unit Price |
    | :----------- | :------- | :--------- |
    | Laptop       | 2        | 1200.50    |
    | Mouse        | 5        | 25.00      |
    | Keyboard     | 3        | 75.99      |
    | Monitor      | 1        | 300.00     |
    | Projector    | 1        | 850.00     |
    | Webcam       | 10       | 45.00      |
    | Headset      | 4        | 99.99      |
    | SSD          | 2        | 180.00     |
    | Router       | 1        | 70.00      |

4. **Run the script:**
    ```bash
    python main.py
    ```
    Then open **`data/output_report.xlsx`** in Excel (formulas are calculated when the file is opened).

## What the Agent Produces (`data/output_report.xlsx`)

| Sheet | Contents |
|-------|----------|
| `SalesData` | Original input data |
| `Raw Data` | Copied data + **Total Revenue** formula column (color scale) + **Status** column (`High Value` highlighted in green) + data bars on Quantity + **Review** dropdown (Pending / Approved / Rejected) + **bar chart** "Revenue by Product" |
| `Summary` | Total / average / highest revenue, total units, count of high-value products (all formulas) + **pie chart** "Revenue Share by Product". Sheet is protected. |
| `Audit Log` | One row per agent action with status colored green / yellow / red |

## Supported Task Types

| type | Key fields |
|------|-----------|
| `copy_data` | `source_sheet`, `dest_sheet` |
| `calculate_column` | `sheet`, `target_column`, `header`, `formula` (use `{row}`), `number_format` |
| `conditional_format` | `sheet`, `range`, `rule_type` (`color_scale`, `data_bar`, `icon_set`, `expression`) |
| `chart` | `sheet`, `chart_type` (`bar`, `line`, `pie`), `data_range`, `category_range`, `title`, `top_left_cell` |
| `summary` | `sheet`, `source_sheet`, `metrics` (`label`, `function`, `column`, `criteria`) |
| `data_validation` | `sheet`, `range`, `validation_type` (`list`, `whole`, `decimal`, `date`, `textLength`) |
| `protect_sheet` | `sheet`, optional `password` |

## Google Sheets Integration (Optional)

1. Create a Google Cloud **Service Account**, enable the Google Sheets API and download its JSON key to `configs/service_account.json` (this file is git-ignored).
2. Share your Google Sheet with the service account's email.
3. `pip install gspread`
4. In the config set `"google_sheets": {"enabled": true, "spreadsheet_id": "<your sheet id>", ...}`.

When disabled (default) the agent simply records "skipped" in the audit log.

## Project Structure

```
agentic-spreadsheet-processor/
├── src/
│   ├── __init__.py
│   ├── spreadsheet_agent.py     # Core agent: task dispatching, Excel manipulation, audit log
│   ├── config_parser.py         # Loads and validates the JSON configuration
│   ├── utils.py                 # Logging and helper functions
│   └── google_sheets_utils.py   # Optional Google Sheets API integration (gspread)
├── configs/
│   └── example_spreadsheet_config.json
├── data/
│   ├── input_data.xlsx          # Sample input Excel file
│   └── output_report.xlsx       # Generated output (git-ignored)
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Debugging Tips

* **`KeyError: 'SheetName'`**: The sheet name in the config does not match the workbook. Check `SalesData` / `Raw Data`.
* **`#NAME?` / `#VALUE!` in Excel**: The formula in the config is not valid Excel syntax. Test it in Excel first.
* **Chart or formatting missing**: Check the ranges in the config and look at the **Audit Log** sheet for `ERROR` rows.
