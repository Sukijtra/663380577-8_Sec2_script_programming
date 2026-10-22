# My Simple Task Manager CLI (Week 7)

A command-line interface (CLI) application for managing your daily tasks.
You can add, list, complete, and delete tasks, and your tasks are saved automatically.

**Topic:** Building a Simple CLI Application, Error Handling & Project Structure

## Features

* **Add Tasks**: Add new tasks with a description.
* **List Tasks**: View all your tasks, showing their ID, description, and status.
* **Complete Tasks**: Mark tasks as completed by their ID.
* **Delete Tasks**: Remove tasks by their ID.
* **Persistence**: Tasks are saved to `data/tasks.json` and loaded automatically.
* **Error Handling**: Invalid input (e.g. typing `abc` as a Task ID, an empty description, or a wrong menu number) shows a message instead of crashing (`try` / `except ValueError`, `json.JSONDecodeError`, `FileNotFoundError`).

## How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
    cd 663380577-8_Sec2_script_programming/my-task-manager
    ```
2. **Run the application** (no external libraries needed):
    ```bash
    python main.py
    ```

### Example session

```
--- Task Manager Menu ---
1. Add Task
2. List Tasks
3. Complete Task
4. Delete Task
5. Exit
-------------------------
Enter your choice (1-5): 1
Enter task description: Buy groceries
Task 'Buy groceries' added with ID 1.
...
Enter your choice (1-5): 3
Enter ID of task to complete: abc
Invalid input. Please enter a number for Task ID.
...
Enter your choice (1-5): 2

--- Your Tasks ---
ID: 1 | Description: Buy groceries | Status: Completed
ID: 2 | Description: Finish Week 7 lab | Status: Pending
------------------
Enter your choice (1-5): 5
Saving tasks and exiting. Goodbye!
```

## Project Structure

```
my-task-manager/
├── src/
│   ├── __init__.py      # Makes 'src' a Python package
│   ├── task_data.py     # Handles reading from/writing to tasks.json
│   └── task_logic.py    # Contains core task management functions (add, list, complete, delete)
├── data/
│   └── tasks.json       # Stores your tasks (created automatically)
├── main.py              # The main entry point of the application
├── .gitignore           # Specifies files/folders to ignore in Git
└── README.md            # This file!
```

## Debugging in VS Code

* **Set a Breakpoint:** Click in the gutter next to `choice = input("Enter your choice (1-5): ").strip()` in `main.py`, or inside `add_task` / `complete_task` in `src/task_logic.py`.
* **Start Debugging:** Open the "Run and Debug" view and choose "Python File".
* **Controls:** Continue (F5), Step Over (F10), Step Into (F11), Step Out (Shift+F11), Restart (Ctrl+Shift+F5), Stop (Shift+F5).
* **Inspect Variables:** Use the "Variables", "Watch" and "Call Stack" panes.
* **Debugging Error Handling:** Put a breakpoint on `int(task_id_str)`, enter `abc` as the Task ID, and watch the debugger jump to the `except ValueError` block.

## Contributing

Feel free to fork this repository, add features, or improve existing ones!

## License

This project is open source. (You might add a specific license here later, e.g., MIT)
