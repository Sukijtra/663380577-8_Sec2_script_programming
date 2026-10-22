
import logging
from pathlib import Path

from src.csv_handler import CSVHandler
from src.json_handler import JSONHandler
from src.utils import ensure_directory_exists, setup_logging


logger = setup_logging(__name__)


def main():
    """Run the CSV and JSON processing workflows."""

    # Set up the data directory and file paths.
    project_dir = Path(__file__).resolve().parent
    data_dir = project_dir / "data"

    ensure_directory_exists(str(data_dir))

    input_csv_path = data_dir / "input_sales.csv"
    output_csv_path = data_dir / "output_filtered_sales.csv"

    input_json_path = data_dir / "input_inventory.json"
    output_json_path = data_dir / "output_updated_inventory.json"

    csv_proc = CSVHandler()
    json_proc = JSONHandler()

    # ---------------- CSV PROCESSING ----------------
    logger.info("Starting CSV processing")

    sales_data = csv_proc.read_csv_as_dicts(str(input_csv_path))

    if sales_data is not None:
        min_amount = 100.0

        results = csv_proc.process_sales_data(
            sales_data,
            min_sale_amount=min_amount
        )

        filtered_sales = results["filtered_sales"]
        summary = results["summary"]

        logger.info(f"Sales summary: {summary}")

        fieldnames = [
            "OrderID",
            "Product",
            "Amount",
            "Price",
            "Customer"
        ]

        summary_row = {
            "OrderID": "SUMMARY",
            "Product": "Total/Avg",
            "Amount": summary["Total Sales"],
            "Price": summary["Average Item Price"],
            "Customer": (
                f"Count: {summary['Filtered Sales Count']}"
            )
        }

        output_data = filtered_sales + [summary_row]

        csv_proc.write_dicts_to_csv(
            output_data,
            str(output_csv_path),
            fieldnames
        )
    else:
        logger.error("CSV processing skipped because input could not be read.")

    # ---------------- JSON PROCESSING ----------------
    logger.info("Starting JSON processing")

    inventory_data = json_proc.read_json(str(input_json_path))

    if inventory_data is not None:
        json_proc.update_inventory(
            inventory_data, "PROD001", 60
        )

        json_proc.update_inventory(
            inventory_data, "PROD003", 75
        )

        new_product = {
            "id": "PROD004",
            "name": "Gaming Headset",
            "category": "Audio",
            "stock": 90,
            "details": {
                "brand": "SoundBlaster",
                "features": [
                    "Noise Cancelling",
                    "RGB"
                ]
            }
        }

        json_proc.add_product(inventory_data, new_product)

        json_proc.write_json(
            inventory_data,
            str(output_json_path),
            indent=2
        )
    else:
        logger.error(
            "JSON processing skipped because input could not be read."
        )

    logger.info("All processing workflows completed.")


if __name__ == "__main__":
    main()
