
import csv
import os

from .utils import setup_logging, ensure_directory_exists


logger = setup_logging(__name__)


class CSVHandler:
    """Read, process, and write CSV data."""

    def read_csv_as_dicts(self, file_path):
        """Read CSV rows as a list of dictionaries."""
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            return None

        try:
            with open(
                file_path, mode="r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)
                data = list(reader)

            logger.info(f"Read {len(data)} rows from {file_path}")
            return data

        except (OSError, csv.Error) as error:
            logger.error(f"Error reading CSV: {error}")
            return None

    def write_dicts_to_csv(self, data, file_path, fieldnames):
        """Write dictionaries to a CSV file."""
        if not data:
            logger.warning("No data provided to write.")
            return False

        ensure_directory_exists(os.path.dirname(file_path))

        try:
            with open(
                file_path, mode="w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames,
                    extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(data)

            logger.info(f"Wrote {len(data)} rows to {file_path}")
            return True

        except (OSError, csv.Error) as error:
            logger.error(f"Error writing CSV: {error}")
            return False

    def process_sales_data(self, sales_data, min_sale_amount=0):
        """Calculate sales totals, average price, and filtered rows."""
        if not sales_data:
            return {"filtered_sales": [], "summary": {}}

        total_sales = 0.0
        total_price = 0.0
        num_items = 0
        filtered_sales = []

        for row in sales_data:
            try:
                amount = float(row.get("Amount", 0))
                price = float(row.get("Price", 0))

                total_sales += amount
                total_price += price
                num_items += 1

                if amount >= min_sale_amount:
                    filtered_sales.append(row)

            except (ValueError, TypeError) as error:
                logger.warning(f"Skipping invalid row {row}: {error}")

        average_price = (
            total_price / num_items if num_items else 0.0
        )

        summary = {
            "Total Sales": f"{total_sales:.2f}",
            "Average Item Price": f"{average_price:.2f}",
            "Filtered Sales Count": len(filtered_sales),
        }

        logger.info(f"Sales summary: {summary}")

        return {
            "filtered_sales": filtered_sales,
            "summary": summary,
        }
