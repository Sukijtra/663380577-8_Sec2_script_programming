# enhanced-task-manager-design/main.py
# Import the main components of our application from the 'src' package.
# (Importing through the package is required because the modules in src/
#  use relative imports such as `from .task import Task`.)
from src.task_manager import TaskManager
from src.cli_interface import CLIInterface


def main():
    """
    Main entry point for the Enhanced Task Manager application.
    Initializes TaskManager and CLIInterface, then starts the CLI loop.
    """
    manager = TaskManager()      # Initialize the core logic manager
    cli = CLIInterface(manager)  # Initialize the CLI interface, passing the manager

    cli.run()  # Start the main command-line interaction loop


if __name__ == "__main__":
    main()
