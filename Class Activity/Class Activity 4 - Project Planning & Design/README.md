# Enhanced Task Manager Design (Week 11 Scaffold)

This project serves as a conceptual and architectural scaffold for an Enhanced Task Manager CLI application.
It demonstrates **Project Planning & Design** principles, breaking down a larger application into modular components before full implementation.

This version is designed to evolve from the previous Task Manager, integrating advanced features like **tags**, **search**, **filtering**, and **sorting**.

📄 **Read the full design document: [PLAN.md](PLAN.md)**

## Key Concepts Demonstrated (Design Focus)

* **Project Planning:** The importance of defining requirements and designing architecture upfront.
* **Modular Design:** Breaking the application into logical, independent components:
    * `task.py`: Defines task data structures (models).
    * `data_persistence.py`: Handles all file I/O (loading/saving).
    * `task_manager.py`: Contains core business logic (managing tasks).
    * `cli_interface.py`: Manages all user interaction (input/output).
    * `main.py`: Orchestrates the application flow.
* **Separation of Concerns:** Each module has a single, clear responsibility.
* **Extensibility:** The design aims to make it easy to add new features or change underlying technologies (e.g., switch from JSON to a database).
* **Requirements Definition**: Outlined in [`PLAN.md`](PLAN.md).

## Features

| Feature | Status |
|---------|--------|
| Basic CRUD: add, list, complete, delete | ✅ Working |
| Task Types: Normal, Due Date, Priority (inheritance + polymorphic `to_dict` / `__str__`) | ✅ Working |
| Tags: multiple tags per task | ✅ Working |
| Persistence: `data/tasks.json`, reloads the correct task type via `_type` | ✅ Working |
| Input validation: date format, priority, non-numeric IDs | ✅ Working |
| Search by keyword in description or tags | 🧩 Placeholder (planned) |
| Filter by status, due date, priority, tags | 🧩 Placeholder (planned) |
| Sort by ID, due date, priority | 🧩 Placeholder (planned) |

## How to Run (Skeleton)

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
    cd "663380577-8_Sec2_script_programming/Class Activity/Class Activity 4 - Project Planning & Design"
    ```
2. **Run the application** (no external libraries needed):
    ```bash
    python main.py
    ```
    (Note: Search, filter and sort are placeholders in this scaffold and will print "DEBUG" messages.)

### Example session

```
--- Enhanced Task Manager Menu ---
1. Add Normal Task
2. Add Due Date Task
3. Add Priority Task
4. List All Tasks
5. Complete Task
6. Delete Task
7. Search Tasks (Placeholder)
8. Filter Tasks (Placeholder)
9. Sort Tasks (Placeholder)
0. Exit
----------------------------------
Enter your choice (0-9): 4

--- Your Tasks ---
ID: 1 | Description: Read lecture notes | Status: Completed | Tags: study, python
ID: 2 | Description: Submit Week 11 lab | Status: Pending | Due: 2026-10-30 | Tags: school, urgent
ID: 3 | Description: Refactor CLI | Status: Pending | Priority: High | Tags: work
ID: 4 | Description: Write PLAN.md | Status: Pending | Priority: Medium
------------------
Enter your choice (0-9): 7
Enter search keyword: python
DEBUG: Search functionality for 'python' not yet implemented.
No tasks found matching 'python'.
```

## Project Structure

```
enhanced-task-manager-design/
├── src/
│   ├── __init__.py           # Makes 'src' a Python package
│   ├── task.py               # Task models (Task, DueDateTask, PriorityTask) with tags
│   ├── data_persistence.py   # Handles JSON file operations
│   ├── task_manager.py       # Core task logic (placeholders for new features)
│   └── cli_interface.py      # Handles user interaction (menu, input/output)
├── data/
│   └── tasks.json            # Stores your tasks (created automatically)
├── main.py                   # Application entry point
├── .gitignore                # Files/folders to ignore in Git
├── README.md                 # This project overview
└── PLAN.md                   # THE KEY DOCUMENT: Detailed project plan and design
```

> **Note:** The modules in `src/` use relative imports (`from .task import Task`), so `main.py` imports them through the package (`from src.task_manager import TaskManager`). Run `python main.py` from the project folder.

## Future Implementation / Extension Ideas

* **Implement Search/Filter/Sort:** Fill out the placeholder methods in `task_manager.py` and integrate them fully into `cli_interface.py`.
* **Advanced Tag Management:** List all unique tags, or delete tasks by tag.
* **Priority Levels:** Numeric priority levels (e.g., 1-5) with sorting.
* **Reminders:** Show upcoming tasks on startup.
* **GUI Interface:** `Tkinter`, `PyQt`, or `Kivy`.
* **Database Integration:** Replace `data_persistence.py` with SQLite.
* **Unit Testing:** Automated tests for `task.py` and `task_manager.py`.

## Contributing

This project is a scaffold. Feel free to fork it and start implementing the planned features!

## License

This project is open source. (You might add a specific license here later, e.g., MIT)
