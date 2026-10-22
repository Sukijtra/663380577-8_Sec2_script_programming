# Project Plan: Enhanced Task Manager CLI

## 1. Introduction

This document outlines the plan for developing an enhanced command-line interface (CLI) Task Manager application. Building upon previous iterations (Week 7 procedural version, Week 8 OOP version), this version will focus on improved modularity, advanced task management features, and a clear separation of concerns to facilitate future development and maintenance.

## 2. Requirements

### 2.1. Functional Requirements (What the system *will do*)

* **Task Management (Core CRUD):**
    * Create new tasks with a description, completion status (default pending), and optional tags.
    * Create specialized tasks:
        * Due Date Tasks: Include a due date (YYYY-MM-DD format).
        * Priority Tasks: Include a priority level (High, Medium, Low).
    * List all tasks, displaying relevant details including type-specific attributes and tags.
    * Mark tasks as completed.
    * Delete tasks by ID.
* **Advanced Task Retrieval:**
    * **Search:** Allow searching tasks by keywords present in their description or tags.
    * **Filter:** Enable filtering tasks by:
        * Completion status (completed/pending).
        * Due date range (e.g., tasks due before/after a specific date).
        * Priority level.
        * Specific tag(s).
    * **Sort:** Allow sorting tasks by:
        * Task ID (default).
        * Due Date (for DueDateTasks).
        * Priority (for PriorityTasks).
        * Creation Date (implicitly by ID for now).
* **Data Persistence:**
    * Automatically save all tasks to a JSON file (`data/tasks.json`) after significant changes (add, complete, delete).
    * Load all tasks from the JSON file on application startup, correctly reconstructing specialized task types.

### 2.2. Non-Functional Requirements (How well the system *will do it*)

* **Usability:** User-friendly command-line interface with clear menus and prompts.
* **Reliability:** Robust error handling for invalid user input (e.g., date formats, non-numeric IDs).
* **Maintainability:** Codebase should be well-structured, commented, and easy to understand for future modifications.
* **Extensibility:** The architecture should allow for easy addition of new task types, filtering criteria, or even switching persistence mechanisms (e.g., to a database) in the future without major refactoring.
* **Performance:** For typical usage (hundreds of tasks), operations should be near-instantaneous.

## 3. High-Level Design / Architecture

The application follows a modular, object-oriented design, separating concerns into distinct Python modules:

```
├── src/
│   ├── task.py               # Data Models (Task, DueDateTask, PriorityTask)
│   ├── data_persistence.py   # Data Storage/Retrieval Layer
│   ├── task_manager.py       # Business Logic Layer (Task Management Operations)
│   ├── cli_interface.py      # User Interface Layer (CLI Input/Output)
│   └── __init__.py           # Python package marker
├── data/                     # Directory for data files
│   └── tasks.json            # Task storage file
├── main.py                   # Application Entry Point / Orchestrator
├── README.md                 # Project overview
└── PLAN.md                   # This planning document
```

### Layer diagram

```
            ┌──────────────────────┐
  user ───▶ │   cli_interface.py   │  UI layer: menus, input, validation, output
            └──────────┬───────────┘
                       │ calls methods
            ┌──────────▼───────────┐
            │   task_manager.py    │  Business logic: add / complete / delete
            │                      │  search / filter / sort (planned)
            └──────────┬───────────┘
                       │ load_tasks() / save_tasks()
            ┌──────────▼───────────┐
            │ data_persistence.py  │  JSON I/O, dict ⇄ Task objects
            └──────────┬───────────┘
                       │
                 data/tasks.json

  task.py (Task ◀── DueDateTask, Task ◀── PriorityTask) is used by every layer.
  main.py creates TaskManager + CLIInterface and calls cli.run().
```

### 3.1. Module Responsibilities

* **`task.py` (Models):**
    * Defines the `Task` base class and its subclasses (`DueDateTask`, `PriorityTask`).
    * Each task class holds its own attributes (id, description, completed, `tags`, due_date, priority).
    * Includes methods for marking complete (`mark_complete`) and managing tags (`add_tag`, `remove_tag`).
    * Handles serialization to Python dictionaries (`to_dict`).
    * Handles string representation for display (`__str__`) and debugging (`__repr__`).
* **`data_persistence.py` (Data Layer):**
    * Encapsulates all file I/O operations (reading from / writing to `tasks.json`).
    * Converts JSON dictionaries back into `Task` objects (and subclasses) using the `_type` field.
    * Converts `Task` objects into dictionaries for saving.
    * Handles file errors (`FileNotFoundError`, `JSONDecodeError`).
* **`task_manager.py` (Business Logic Layer):**
    * Manages the collection of `Task` objects.
    * Uses `DataPersistence` to load and save tasks, but does not directly interact with files.
    * Provides methods for core operations: `add_normal_task`, `add_due_date_task`, `add_priority_task`, `complete_task`, `delete_task`, `get_all_tasks`.
    * **Will implement the logic for new features:** `search_tasks`, `filter_tasks`, `sort_tasks`.
    * Maintains `next_id` for new tasks.
* **`cli_interface.py` (User Interface Layer):**
    * Responsible solely for user interaction: displaying menus, prompting for input, validating input formats, and displaying output messages.
    * Calls methods on the `TaskManager` object to perform operations.
    * Does not contain business logic.
* **`main.py` (Orchestrator):**
    * The entry point of the application.
    * Initializes `TaskManager` and `CLIInterface`.
    * Starts the main application loop by calling `cli.run()`.

### 3.2. Data Model Changes

* **`Task` Class:**
    * New attribute: `tags` (list of strings).
* **JSON Structure:**
    * Each task dictionary in `tasks.json` now has a `tags` key and a `_type` key:

```json
{
    "id": 2,
    "description": "Submit Week 11 lab",
    "completed": false,
    "tags": ["school", "urgent"],
    "_type": "DueDateTask",
    "due_date": "2026-10-30"
}
```

### 3.3. Interface Design (CLI Menu)

```
1. Add Normal Task      4. List All Tasks       7. Search Tasks (Placeholder)
2. Add Due Date Task    5. Complete Task        8. Filter Tasks (Placeholder)
3. Add Priority Task    6. Delete Task          9. Sort Tasks (Placeholder)
0. Exit
```

## 4. Implementation Plan (High-Level)

This week's focus is the design. Subsequent weeks will involve:

1. **Refactor Existing Code:** Migrate existing `Task`, `DueDateTask`, `PriorityTask` logic into `src/task.py`. ✅
2. **Implement `data_persistence.py`:** Move JSON loading/saving logic from `TaskManager` to this new module. Update `TaskManager` to use `DataPersistence`. ✅
3. **Implement `cli_interface.py`:** Move all `print` statements and `input` calls from `main.py` and `TaskManager` into this new module. Refactor `main.py` to orchestrate. ✅
4. **Implement Tags:** Fully integrate the `tags` attribute into `Task` and its subclasses, including user input/display. ✅
5. **Implement Search:** Fill out `search_tasks` in `task_manager.py` and add menu options in `cli_interface.py`.
6. **Implement Filter:** Fill out `filter_tasks` in `task_manager.py` and add menu options.
7. **Implement Sort:** Fill out `sort_tasks` in `task_manager.py` and add menu options.

### Pseudocode for the planned features

```
search_tasks(keyword):
    k = keyword.lower()
    return tasks where k in description.lower() OR any(k in tag.lower() for tag in tags)

filter_tasks(status, due_date_before, priority, tags):
    result = all tasks
    if status is given:          keep tasks where completed == status
    if due_date_before is given: keep DueDateTasks where due_date <= due_date_before
    if priority is given:        keep PriorityTasks where priority == priority
    if tags is given:            keep tasks that have every tag in tags
    return result

sort_tasks(criterion, reverse):
    id       -> key = task.id
    due_date -> key = task.due_date, tasks without a due date go last (date.max)
    priority -> key = {"High": 1, "Medium": 2, "Low": 3}[priority], others go last (99)
    return sorted(tasks, key, reverse)
```

## 5. Potential Challenges & Considerations

* **Date Range Filtering:** Designing flexible date range inputs (e.g., "tasks due next week").
* **Sorting Logic:** Handling sorting across different task types (e.g., how to sort a normal `Task` by due date when it has none).
* **CLI Complexity:** Keeping the CLI intuitive as more features are added.
* **Error Handling:** Ensuring all user inputs and file operations are robustly handled.

## 6. Future Enhancements (Beyond this plan)

* **Reminders:** Display reminders for upcoming due dates (e.g., on startup).
* **User Accounts:** Basic user authentication so multiple users can manage their own tasks.
* **GUI Interface:** Build a graphical user interface using Tkinter or PyQt.
* **Database Integration:** Replace JSON persistence with a SQLite database.
* **Export/Import:** Export tasks to CSV or other formats.
* **Undo/Redo:** Implement an "undo" stack for recent operations.
