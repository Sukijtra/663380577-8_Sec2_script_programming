# agentic-data-processor/src/data_agent.py
import os
import json
import datetime
from .utils import setup_logging, log_audit_entry, ensure_directory_exists
from .csv_tasks import CSVTasks
from .json_tasks import JSONTasks
from .conversion_tasks import ConversionTasks

logger = setup_logging(__name__)


class DataAgent:
    """
    An agent that processes various data formats (CSV, JSON) based on a structured
    configuration file, managing internal data state.
    """
    def __init__(self, config, base_dir="."):
        self.config = config
        self.base_dir = base_dir
        self.audit_log = []
        self.data_store = {}  # Stores intermediate data results {key: data_object}
        self.start_time = datetime.datetime.now()

        self.csv_tasks = CSVTasks()
        self.json_tasks = JSONTasks()
        self.conversion_tasks = ConversionTasks()

        # Task dispatcher: maps task "type" from the config to a handler method
        self.handlers = {
            "load_csv": self._handle_load_csv,
            "save_csv": self._handle_save_csv,
            "transform_csv_aggregate": self._handle_aggregate,
            "filter_csv": self._handle_filter,
            "load_json": self._handle_load_json,
            "save_json": self._handle_save_json,
            "update_json_data": self._handle_update_json,
            "query_json_data": self._handle_query_json,
            "csv_to_json_conversion": self._handle_csv_to_json,
            "json_to_csv_conversion": self._handle_json_to_csv,
        }
        logger.info("Data Agent initialized with configuration.")

    def _get_data_from_store(self, key):
        """Retrieves data from the data store."""
        if key not in self.data_store:
            logger.error(f"Data key '{key}' not found in agent's data store.")
            return None
        return self.data_store[key]

    def _set_data_in_store(self, key, data):
        """Stores data in the data store."""
        self.data_store[key] = data
        logger.debug(f"Data stored under key: '{key}'.")

    def _path(self, task):
        """Resolves a task's file_path relative to the project root."""
        return os.path.join(self.base_dir, task["file_path"])

    # --- Task handlers: each returns (success, output_data) ---
    def _handle_load_csv(self, task, data):
        output = self.csv_tasks.load_csv(self._path(task))
        return output is not None, output

    def _handle_save_csv(self, task, data):
        # Fall back to fieldnames remembered from a json_to_csv_conversion task
        fieldnames = task.get("fieldnames") or self.data_store.get(f"{task['input_data_key']}__fieldnames")
        return self.csv_tasks.save_csv(data, self._path(task), fieldnames), None

    def _handle_aggregate(self, task, data):
        output = self.csv_tasks.transform_csv_aggregate(
            data, task.get("group_by_field"), task.get("aggregate_field"), task.get("aggregate_type", "sum"))
        return output is not None, output

    def _handle_filter(self, task, data):
        output = self.csv_tasks.filter_csv(data, task.get("filter_field"), task.get("operator"), task.get("value"))
        return output is not None, output

    def _handle_load_json(self, task, data):
        output = self.json_tasks.load_json(self._path(task))
        return output is not None, output

    def _handle_save_json(self, task, data):
        return self.json_tasks.save_json(data, self._path(task), task.get("indent", 2)), None

    def _handle_update_json(self, task, data):
        output = self.json_tasks.update_json_data(data, task.get("updates", []))
        return output is not None, output

    def _handle_query_json(self, task, data):
        path = task.get("path")
        result = self.json_tasks.query_json_data(data, path)
        log_audit_entry(self.audit_log, "INFO", f"Query result for path '{path}': {result}",
                        task["type"], {"query_path": path, "result": result})
        # A query that finds nothing is still a successful run
        return True, result

    def _handle_csv_to_json(self, task, data):
        output = self.conversion_tasks.csv_to_json(data)
        return output is not None, output

    def _handle_json_to_csv(self, task, data):
        rows, fieldnames = self.conversion_tasks.json_to_csv(data, task.get("fieldnames"))
        # Remember the column order so a later save_csv task can use it
        if task.get("output_data_key"):
            self._set_data_in_store(f"{task['output_data_key']}__fieldnames", fieldnames)
        return True, rows

    def _process_task(self, task):
        """Dispatches a task to the appropriate handler and manages data state."""
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        input_data_key = task.get("input_data_key")    # Key to retrieve input data from store
        output_data_key = task.get("output_data_key")  # Key to store output data in store

        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type, task)

        handler = self.handlers.get(task_type)
        if handler is None:
            log_audit_entry(self.audit_log, "WARNING", f"Unsupported task type: {task_type}", task_type, task)
            logger.warning(f"Unsupported task type: {task_type}")
            return

        current_data = None
        if input_data_key:
            current_data = self._get_data_from_store(input_data_key)
            if current_data is None:
                log_audit_entry(self.audit_log, "ERROR",
                                f"Task '{task_name}' failed: Required input data '{input_data_key}' not found in store.",
                                task_type, task)
                return

        try:
            success, task_output_data = handler(task, current_data)

            # Store the output data if the task was successful and produced data
            if success and task_output_data is not None and output_data_key:
                self._set_data_in_store(output_data_key, task_output_data)

            if success:
                log_audit_entry(self.audit_log, "SUCCESS", f"Task '{task_name}' completed successfully.", task_type, task)
            else:
                log_audit_entry(self.audit_log, "ERROR", f"Task '{task_name}' failed.", task_type, task)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"An error occurred during task '{task_name}': {e}",
                            task_type, {"error": str(e), "task_details": task})
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)

    def _generate_audit_report(self, output_dir="reports"):
        """Generates a JSON audit report."""
        ensure_directory_exists(output_dir)
        report_filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(output_dir, report_filename)
        try:
            log_audit_entry(self.audit_log, "INFO", f"Audit report generated at {report_path}", "audit_report")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=4, ensure_ascii=False)
            logger.info(f"Audit report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")
        return report_path

    def run(self):
        """Executes all tasks defined in the configuration."""
        logger.info("Starting Data Agent run...")
        log_audit_entry(self.audit_log, "INFO", "Data Agent started.", "agent_run")

        for task in self.config.get("tasks", []):
            self._process_task(task)

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        log_audit_entry(self.audit_log, "INFO", f"Data Agent finished in {duration:.2f} seconds.", "agent_run_summary")
        logger.info(f"Data Agent finished. Total time: {duration:.2f} seconds.")

        # Save audit report in a dedicated 'reports' subfolder within the project root
        return self._generate_audit_report(os.path.join(self.base_dir, 'reports'))
