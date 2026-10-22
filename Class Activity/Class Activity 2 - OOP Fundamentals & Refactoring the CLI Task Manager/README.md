# My OOP Task Manager CLI (Week 8)

A command-line interface (CLI) application for managing your daily tasks, built with Object-Oriented Programming (OOP) principles.
This version refactors the previous procedural approach (Week 7) into a more organized and scalable structure using `Task` and `TaskManager` classes.

**Topic:** Object-Oriented Programming (OOP) Fundamentals & Refactoring the CLI Task Manager

## Features

* **Add Tasks**: Add new tasks with a description.
* **List Tasks**: View all your tasks, showing their ID, description, and status.
* **Complete Tasks**: Mark tasks as completed by their ID.
* **Delete Tasks**: Remove tasks by their ID.
* **Persistence**: Tasks are saved to `data/tasks.json` after every change and loaded automatically upon startup.

## OOP Design

* **`Task` Class** (`src/task.py`): Represents an individual task.
    * Attributes: `id`, `description`, `completed`
    * Methods: `mark_complete()`, `to_dict()` (for saving to JSON), `__str__` (for `print`), `__repr__` (for debugging)
* **`TaskManager` Class** (`src/task_manager.py`): Manages the collection of `Task` objects.
    * Attributes: `self.tasks` (list of `Task` objects), `self.next_id`
    * Methods: `add_task()`, `list_tasks()`, `complete_task()`, `delete_task()`, plus internal `_load_tasks()` / `_save_tasks()`
    * Converts `Task` objects ⇄ dictionaries when saving/loading JSON.

```
Task(id=1, description='Learn OOP classes', completed=False)   # repr(task)
ID: 1 | Description: Learn OOP classes | Status: Pending        # print(task)
```

## How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
    cd "663380577-8_Sec2_script_programming/Class Activity/Class Activity 2 - OOP Fundamentals & Refactoring the CLI Task Manager"
    ```
2. **Run the application** (no external libraries needed):
    ```bash
    python main.py
    ```

> **Note:** `task_manager.py` uses a relative import (`from .task import Task`), so `main.py` imports it through the package: `from src.task_manager import TaskManager`. Always run `python main.py` from the project folder.

### Example session

```
Enter your choice (1-5): 1
Enter task description: Learn OOP classes
Task 'Learn OOP classes' added with ID 1.
Enter your choice (1-5): 3
Enter ID of task to complete: 1
Task ID 1 marked as completed.
Enter your choice (1-5): 4
Enter ID of task to delete: 99
Error: Task with ID 99 not found.
Enter your choice (1-5): 2

--- Your Tasks ---
ID: 1 | Description: Learn OOP classes | Status: Completed
ID: 2 | Description: Refactor task manager | Status: Pending
------------------
```

## Project Structure

```
my-oop-task-manager/
├── src/
│   ├── __init__.py       # Makes 'src' a Python package
│   ├── task.py           # Defines the Task class
│   └── task_manager.py   # Defines the TaskManager class (handles all core logic and data)
├── data/
│   └── tasks.json        # Stores your tasks (created automatically)
├── main.py               # The main entry point of the application
├── .gitignore            # Specifies files/folders to ignore in Git
└── README.md             # This file!
```

## Debugging in VS Code (with OOP Focus)

* **Set Breakpoints:** on `manager = TaskManager()` in `main.py`, inside `__init__` and `_load_tasks` in `src/task_manager.py`, and inside `__init__` and `mark_complete` in `src/task.py`.
* **Observe Object Creation:** At `manager = TaskManager()` press **Step Into (F11)** to enter `TaskManager.__init__`, then `_load_tasks`, then `Task.__init__`.
* **Understanding `self`:** In the "Variables" pane, expand `self` to see the attributes of the current object. When you complete a task, step into `task.mark_complete()` and watch `self.completed` change to `True` on that specific instance.

## Contributing

Feel free to fork this repository, add features, or improve existing ones!

## License

This project is open source. (You might add a specific license here later, e.g., MIT)
