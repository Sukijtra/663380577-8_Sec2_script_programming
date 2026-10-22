# Week 8: Agentic Data Processing (Advanced CSV & JSON Workflows)

This project demonstrates an "Agentic Data Processor" that orchestrates complex data manipulation workflows for CSV and JSON files based on a declarative JSON configuration. It showcases advanced data transformation, cross-format conversion, and robust state management within the agent.

## Key Concepts Demonstrated

* **Agentic Workflow Orchestration**: The `DataAgent` reads a pipeline defined in `configs/data_pipeline_config.json` and executes tasks sequentially, managing the flow of data between steps.
* **Internal Data Store**: The agent keeps an in-memory `data_store` to pass intermediate data between tasks using `input_data_key` / `output_data_key`.
* **Task Dispatcher**: A dictionary maps each task `type` in the config to its handler method.
* **Advanced CSV Processing**: Loading (`DictReader`), **aggregation** (sum / count / average grouped by a field), **filtering** (`>`, `<`, `>=`, `<=`, `==`, `!=`) and saving (`DictWriter`).
* **Advanced JSON Processing**: Loading/saving, **dynamic updates** on nested data with dot-notation paths (`set`, `add_to_list`, `remove_from_list`) and **querying** nested values. List items can be addressed by index (`0.stock`) or by `id` (`PROD001.details.color`).
* **Cross-Format Conversion**: CSV → JSON (with automatic number/boolean/null conversion) and JSON → CSV (flattening nested keys such as `details.brand`).
* **Robustness**: Error handling around every task and a JSON **audit report** that records each step.

## Setup & How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
   cd 663380577-8_Sec2_script_programming/agentic-data-processor
   ```
2. **Install Dependencies:**
   Only built-in Python modules (`csv`, `json`, `logging`) are used. A virtual environment is still recommended:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   ```
3. **Input data** is already provided in `data/input_sales.csv` and `data/input_inventory.json`.
4. **Run the script:**
   ```bash
   python main.py
   ```

The pipeline in `data_pipeline_config.json` will:

1. Load `input_sales.csv`.
2. Aggregate sales by customer → `data/processed_sales_by_customer.csv`.
3. Filter high-value orders (`Amount >= 100`) into the data store.
4. Convert the raw sales data to JSON → `data/sales_data.json`.
5. Load `input_inventory.json`.
6. Update stock, change nested details, add a new product (`PROD004`) and add a feature to its list.
7. Query a nested value (`0.details.brand` → `TechCorp`).
8. Save the modified inventory → `data/updated_inventory.json`.
9. Write an audit report → `reports/audit_report_YYYYMMDD_HHMMSS.json`.

### Example output (`data/processed_sales_by_customer.csv`)

```
Customer,Total_Amount
Alice,1425.75
Bob,130.75
Charlie,500.0
David,90.0
Eve,15.5
```

## Supported Task Types

| type | Required fields | What it does |
|------|-----------------|--------------|
| `load_csv` | `file_path`, `output_data_key` | Read CSV into a list of dicts |
| `save_csv` | `file_path`, `input_data_key` (`fieldnames` optional) | Write list of dicts to CSV |
| `transform_csv_aggregate` | `input_data_key`, `output_data_key`, `group_by_field`, `aggregate_field`, `aggregate_type` | Group + sum / count / average |
| `filter_csv` | `input_data_key`, `output_data_key`, `filter_field`, `operator`, `value` | Keep matching rows |
| `load_json` | `file_path`, `output_data_key` | Read a JSON file |
| `save_json` | `file_path`, `input_data_key` (`indent` optional) | Write JSON |
| `update_json_data` | `input_data_key`, `output_data_key`, `updates` | Apply set / add / remove operations |
| `query_json_data` | `input_data_key`, `output_data_key`, `path` | Read one nested value |
| `csv_to_json_conversion` | `input_data_key`, `output_data_key` | CSV rows → typed JSON objects |
| `json_to_csv_conversion` | `input_data_key`, `output_data_key` | JSON objects → flat CSV rows |

## Project Structure

```
agentic-data-processor/
├── src/
│   ├── __init__.py
│   ├── data_agent.py          # Core agent: dispatches tasks and manages the data store
│   ├── csv_tasks.py           # Load, save, aggregate, filter CSV
│   ├── json_tasks.py          # Load, save, update, query JSON
│   ├── conversion_tasks.py    # CSV <-> JSON conversions
│   ├── config_parser.py       # Loads and validates the pipeline configuration
│   └── utils.py               # Logging, directory helper, audit logging
├── configs/
│   └── data_pipeline_config.json
├── data/
│   ├── input_sales.csv
│   ├── input_inventory.json
│   ├── processed_sales_by_customer.csv   # Output (generated)
│   ├── sales_data.json                   # Output (generated)
│   └── updated_inventory.json            # Output (generated)
├── main.py
├── .gitignore
└── README.md
```

## Debugging Tips

* **`FileNotFoundError`**: Check that `file_path` values in the config are relative to the project root and the files exist.
* **Task fails with "input data not found"**: The `output_data_key` of an earlier task must match the `input_data_key` of the later task.
* **JSON update skipped**: Check the dot-notation path in the console log; the agent logs a warning for every path it cannot follow.
* **Audit report**: Every run writes `reports/audit_report_*.json` with the status of each step.
