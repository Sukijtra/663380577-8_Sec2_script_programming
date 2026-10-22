# agentic-data-processor/src/json_tasks.py
import copy
import json
import os
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class JSONTasks:
    """
    Handles advanced reading, writing, and manipulation of JSON data.
    """
    def __init__(self):
        logger.info("JSONTasks initialized.")

    def load_json(self, file_path):
        """Loads a JSON file and returns the Python object."""
        if not os.path.exists(file_path):
            logger.error(f"JSON file not found: {file_path}")
            return None
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded JSON from '{file_path}'.")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in '{file_path}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading JSON file '{file_path}': {e}")
            return None

    def save_json(self, data, file_path, indent=2):
        """Saves a Python object to a JSON file, with pretty-printing."""
        ensure_directory_exists(os.path.dirname(file_path))
        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            logger.info(f"Successfully saved JSON to '{file_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file '{file_path}': {e}")
            return False

    def _step(self, node, key):
        """
        Moves one level down a JSON structure.
        For lists, `key` can be an index ("0") or the "id" of an item ("PROD001").
        Returns None when the key cannot be followed.
        """
        if isinstance(node, dict):
            return node.get(key)
        if isinstance(node, list):
            if key.isdigit():
                index = int(key)
                return node[index] if 0 <= index < len(node) else None
            for item in node:
                if isinstance(item, dict) and item.get("id") == key:
                    return item
        return None

    def _resolve_parent(self, data, keys):
        """Walks the path down to the parent of the last key."""
        node = data
        for key in keys[:-1]:
            node = self._step(node, key)
            if node is None:
                return None
        return node

    def update_json_data(self, data, updates):
        """
        Applies updates to a JSON-like Python object.
        `updates` is a list of dicts: [{"path": "key1.key2", "value": "new_value", "operation": "set"}, ...]
        Supported operations: 'set', 'add_to_list', 'remove_from_list'.
        An empty path ("") means the root object itself (e.g. adding an item to the top-level list).
        """
        if not data:
            logger.warning("No JSON data provided for update.")
            return data

        modified_data = copy.deepcopy(data)  # Deep copy to avoid modifying original reference

        for update in updates or []:
            path = update.get("path", "")
            value = update.get("value")
            operation = update.get("operation", "set")
            try:
                if operation in ("add_to_list", "remove_from_list"):
                    target = modified_data
                    for key in [k for k in path.split('.') if k]:
                        target = self._step(target, key)
                        if target is None:
                            break
                    if not isinstance(target, list):
                        logger.warning(f"Cannot '{operation}' for path '{path}': target is not a list. Skipping update: {update}")
                        continue
                    if operation == "add_to_list":
                        target.append(value)
                        logger.info(f"Added item to list at '{path or '<root>'}'.")
                    elif value in target:
                        target.remove(value)
                        logger.info(f"Removed '{value}' from list at '{path or '<root>'}'.")
                    else:
                        logger.warning(f"Value '{value}' not found in list at '{path}'. Skipping remove: {update}")

                elif operation == "set":
                    if not path:
                        logger.warning(f"Update skipped: 'set' needs a non-empty 'path': {update}")
                        continue
                    keys = path.split('.')
                    parent = self._resolve_parent(modified_data, keys)
                    target_key = keys[-1]
                    if isinstance(parent, dict):
                        parent[target_key] = value
                        logger.info(f"Set '{path}' to '{value}'.")
                    elif isinstance(parent, list) and target_key.isdigit() and int(target_key) < len(parent):
                        parent[int(target_key)] = value
                        logger.info(f"Set '{path}' (list index) to '{value}'.")
                    else:
                        logger.warning(f"Path '{path}' not found. Skipping update: {update}")

                else:
                    logger.warning(f"Unsupported operation '{operation}' for path '{path}'. Skipping update: {update}")
            except Exception as e:
                logger.error(f"Error applying JSON update for path '{path}': {e}. Update: {update}")

        return modified_data

    def query_json_data(self, data, path):
        """
        Queries a specific element from nested JSON data using a dot-notation path.
        Returns the value or None if not found.
        """
        if not data:
            logger.warning("No JSON data to query.")
            return None

        current_node = data
        for key in path.split('.'):
            current_node = self._step(current_node, key)
            if current_node is None:
                logger.warning(f"Query path '{path}' failed at key '{key}'.")
                return None

        logger.info(f"Successfully queried '{path}'. Result: {current_node}")
        return current_node
