# my-task-manager/src/task_data.py
import json
import os

TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'tasks.json')


def load_tasks():
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
        return []
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
        return []
    except FileNotFoundError:
        # This should ideally be caught by os.path.exists, but good to have a fallback
        return []


def save_tasks(tasks):
    """Saves tasks to the JSON file."""
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)  # Ensure directory exists
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4)  # Use indent for pretty printing JSON
