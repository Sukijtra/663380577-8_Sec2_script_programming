# my-task-manager/src/task_logic.py


def get_next_task_id(tasks):
    """Generates a unique ID for a new task."""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1


def add_task(tasks, description):
    """Adds a new task to the list."""
    task_id = get_next_task_id(tasks)
    new_task = {
        "id": task_id,
        "description": description,
        "completed": False
    }
    tasks.append(new_task)
    print(f"Task '{description}' added with ID {task_id}.")
    return tasks


def list_tasks(tasks):
    """Lists all tasks with their status."""
    if not tasks:
        print("No tasks found.")
        return

    print("\n--- Your Tasks ---")
    for task in tasks:
        status = "Completed" if task['completed'] else "Pending"
        print(f"ID: {task['id']} | Description: {task['description']} | Status: {status}")
    print("------------------")


def complete_task(tasks, task_id):
    """Marks a task as completed."""
    found = False
    for task in tasks:
        if task['id'] == task_id:
            if task['completed']:
                print(f"Task ID {task_id} is already completed.")
            else:
                task['completed'] = True
                print(f"Task ID {task_id} marked as completed.")
            found = True
            break
    if not found:
        print(f"Error: Task with ID {task_id} not found.")
    return tasks


def delete_task(tasks, task_id):
    """Deletes a task from the list."""
    original_len = len(tasks)
    tasks[:] = [task for task in tasks if task['id'] != task_id]  # Reassigns list in-place
    if len(tasks) < original_len:
        print(f"Task ID {task_id} deleted successfully.")
    else:
        print(f"Error: Task with ID {task_id} not found.")
    return tasks
