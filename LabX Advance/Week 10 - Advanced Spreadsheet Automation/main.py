# agentic-spreadsheet-processor/main.py
import os

from src.config_parser import ConfigParser
from src.spreadsheet_agent import SpreadsheetAgent
from src.utils import setup_logging

# Set up main logger
logger = setup_logging(__name__)


def main():
    """
    Main entry point for the Agentic Spreadsheet Processor.
    Loads config and runs the agent.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'configs', 'example_spreadsheet_config.json')

    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(base_dir, 'data'), exist_ok=True)

        logger.info(f"Loading configuration from: {config_file_path}")
        config = ConfigParser(config_file_path).load_config()

        # Paths in the config are relative to the project root
        for key in ("input_file", "output_file"):
            config[key] = os.path.join(base_dir, config[key])
        if "credentials_file" in config.get("google_sheets", {}):
            config["google_sheets"]["credentials_file"] = os.path.join(base_dir, config["google_sheets"]["credentials_file"])

        if not os.path.exists(config["input_file"]):
            logger.critical(f"Input Excel file not found: '{config['input_file']}'. Please create it with sample data.")
            logger.info("Refer to the README.md for example content and file structure.")
            return

        logger.info("Initializing Spreadsheet Agent...")
        agent = SpreadsheetAgent(config)

        logger.info("Running Spreadsheet Agent...")
        if agent.run():
            logger.info(f"Done! Open the report: {config['output_file']}")

    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
        logger.info("Please ensure all specified input files and configurations exist.")
    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
        logger.info("Please check the format and required fields in your config file.")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during execution: {e}", exc_info=True)


if __name__ == "__main__":
    main()
