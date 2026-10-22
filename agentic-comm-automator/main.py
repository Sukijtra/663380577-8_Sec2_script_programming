# agentic-comm-automator/main.py
import os
import sys

from src.config_parser import ConfigParser
from src.communication_agent import CommunicationAgent
from src.utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


def check_required_files(config, base_dir):
    """
    Checks if the attachment files listed in send_email tasks exist.
    Paths containing {placeholders} are only known at run time, so they are skipped here.
    """
    missing_files = []
    for task in config['tasks']:
        if task['type'] != 'send_email':
            continue
        for att_path in task.get('parameters', {}).get('attachments', []):
            if '{' in att_path:
                continue
            file_path = os.path.join(base_dir, att_path)
            if not os.path.exists(file_path):
                missing_files.append(file_path)
    return not missing_files, missing_files


def main():
    """
    Main entry point for the Agentic Communication Automator.
    Loads config and runs the agent.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'configs', 'comm_pipeline_config.json')

    try:
        # Ensure data, configs and reports directories exist
        for folder in ('data', 'data/reports', 'data/attachments', 'data/incoming_attachments', 'configs', 'reports'):
            ensure_directory_exists(os.path.join(base_dir, folder))

        logger.info(f"Loading configuration from: {config_file_path}")
        config = ConfigParser(config_file_path).load_config()

        # Check for required attachment files before starting
        files_exist, missing = check_required_files(config, base_dir)
        if not files_exist:
            logger.critical(f"One or more required attachment files are missing: {', '.join(missing)}. Please create them as per README.md.")
            sys.exit(1)

        logger.info("Initializing Communication Agent...")
        agent = CommunicationAgent(config, base_dir)  # Pass base_dir to agent for path resolution

        logger.info("Running Communication Agent workflow...")
        agent.run()
        logger.info("Communication automation process completed.")

    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
        logger.info("Please ensure all specified input files and configurations exist.")
    except ValueError as e:
        logger.critical(f"Configuration or environment variable error: {e}")
        logger.info("Please check the format and required fields in your config file and .env.")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
