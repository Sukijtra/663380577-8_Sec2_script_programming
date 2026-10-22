
import json
import os

from .utils import setup_logging, ensure_directory_exists


logger = setup_logging(__name__)


class JSONHandler:
    """Read, write, and update JSON inventory data."""

    def read_json(self, file_path):
        """Read a JSON file and return a Python object."""
        if not os.path.exists(file_path):
            logger.error(f"JSON file not found: {file_path}")
            return None

        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                data = json.load(file)

            logger.info(f"Read JSON from {file_path}")
            return data

        except json.JSONDecodeError as error:
            logger.error(f"Invalid JSON format: {error}")
            return None

        except OSError as error:
            logger.error(f"Error reading JSON: {error}")
            return None

    def write_json(self, data, file_path, indent=4):
        """Write a Python object to a JSON file."""
        directory = os.path.dirname(file_path)
        ensure_directory_exists(directory)

        try:
            with open(file_path, mode="w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=indent,
                    ensure_ascii=False
                )

            logger.info(f"Wrote JSON to {file_path}")
            return True

        except (OSError, TypeError, ValueError) as error:
            logger.error(f"Error writing JSON: {error}")
            return False

    def update_inventory(self, inventory_data, product_id, new_stock_level):
        """Update the stock of an existing product."""
        if not isinstance(inventory_data, list):
            logger.warning("Inventory data must be a list.")
            return False

        for product in inventory_data:
            if product.get("id") == product_id:
                product["stock"] = new_stock_level
                logger.info(
                    f"Updated {product_id} stock to {new_stock_level}"
                )
                return True

        logger.warning(f"Product {product_id} was not found.")
        return False

    def add_product(self, inventory_data, new_product):
        """Add a new product to the inventory list."""
        if not isinstance(inventory_data, list):
            logger.warning("Inventory data must be a list.")
            return False

        if any(
            product.get("id") == new_product.get("id")
            for product in inventory_data
        ):
            logger.warning("Product ID already exists.")
            return False

        inventory_data.append(new_product)
        logger.info(f"Added product: {new_product.get('name')}")
        return True
