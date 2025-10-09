import os # We use this to get the current working directory for the task file
import json
from sys import platform

# --- CONFIGURATION ---
# The name of the file where tasks will be saved.
TASK_FILE = "todos.json" 
# Prefix for completed tasks.
DONE_MARKER = "[x]"
# Prefix for incomplete tasks.
PENDING_MARKER = "[!]"

#ANSI color codes for priority display(win, mac and linux)
class Colors:
    """Class to hold ANSI color codes"""
    if platform.startswith('win'):
        # On Windows, try to use the ENABLE_VIRTUAL_TERMINAL_PROCESSING sequence
        # For modern terminals like VS Code, these work fine.
        HIGH = '\033[91m' # Light Red
        MEDIUM = '\033[93m' # Light Yellow
        LOW = '\033[92m' # Light Green
        END = '\033[0m' # Reset color
    else:
        # Standard ANSI colors for Linux/macOS
        HIGH = '\033[91m'
        MEDIUM = '\033[93m'
        LOW = '\033[92m'
        END = '\033[0m'

def get_priority_label(priority):
    """Returns the priority label wrapped in ANSI color codes."""
    priority = priority.upper()
    if priority == 'HIGH':
        return f"{Colors.HIGH}[HIGH]{Colors.END}"
    elif priority == 'MEDIUM':
        return f"{Colors.MEDIUM}[MED]{Colors.END}"
    elif priority == 'LOW':
        return f"{Colors.LOW}[LOW]{Colors.END}"
    return "[NONE]"


def load_tasks():
    """Loads tasks from the TASK_FILE(json format), returning a list of task dictionaries."""
    try:
        # 'r' mode means read-only. using json to load the structured data
        with open(TASK_FILE, 'r') as f:
            # .strip() removes any leading/trailing whitespace (like newlines)
            tasks = json.load(f)
        return tasks
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty list.
        return []
    except json.JSONDecodeError:
        # handles the error when the file is present but it is empty
        print(f"Warning: {TASK_FILE} is corrupt or empty")
        return []


def save_tasks(tasks):
    """Saves the current list of tasks to the TASK_FILE (json format)"""
    # 'w' mode means write-mode. It overwrites the file completely.
    #using json.dump for structured data writing
    with open(TASK_FILE, 'w') as f:
        for task in tasks:
            # the indent=4 makes the json files readable clearly
            json.dump(tasks, f, indent=4)

def sort_tasks_by_priority(tasks):
    """
    Sorts the list of task dictionaries based on priority level: HIGH, MEDIUM, LOW, None.
    Uses the list.sort() method with a lambda function for custom sorting.
    """
    # Define the desired order for sorting (numerical order for keys)
    priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'NONE': 4}

    # The lambda function defines the custom sorting key for each task dictionary.
    # We use .get('priority', 'NONE') to safely handle tasks without a priority key.
    # The final .get(..., 5) ensures unknown priorities always go last.
    tasks.sort(key=lambda task: priority_order.get(task.get('priority', 'NONE').upper(), 5))
    
    return tasks

def view_tasks(tasks):
    """Displays the list of tasks with their index."""
    if not tasks:
        print("\n--- Your To-Do List is Empty! ---\n")
        return
    # Sort the tasks before displaying them so High priority is always on top.
    # We sort a copy of the list so we don't permanently change the order in memory
    # until the user saves/quits.

    tasks_to_display = sort_tasks_by_priority(tasks.copy())

    print("\n==================================")
    print("        CURRENT TO-DO LIST        ")
    print("==================================")
    
    # Enumerate provides both the index (starting at 0) and the item.
    for index, task in enumerate(tasks_to_display):
        # Determine the status marker based on the 'done' boolean
        status_marker = DONE_MARKER if task.get('done', False) else PENDING_MARKER
        
        # Get the styled priority label
        priority_label = get_priority_label(task.get('priority', ''))
        
        # Display: Index. [Status] [Priority] Description
        print(f"[{index + 1}.] {status_marker} {priority_label} {task['description']}")
    
    print("=======================================================\n")


def add_task(tasks, new_task_desc, priority):
    """Adds a new task (as a dictionary) to the list with the PENDING status and priority."""
    if new_task_desc.strip():
        new_task = {
            'description': new_task_desc.strip(),
            'done': False,
            'priority': priority.upper()
        }
        tasks.append(new_task)
        save_tasks(tasks)
        print(f"✅ Added task: '{new_task['description']}' with {new_task['priority']} priority.")
    else:
        print("❌ Task description cannot be empty.")

def mark_task_done(tasks, task_index):
    """Marks a task as complete."""
    # Since tasks are displayed sorted, we must sort the list to find the correct index!
    sorted_tasks = sort_tasks_by_priority(tasks.copy())

    try:
        # Convert user index (1-based) to list index (0-based)
        index = task_index - 1
        
        if 0 <= index < len(sorted_tasks):
            # 1. Find the unique task dictionary based on the sorted list
            task_to_mark = sorted_tasks[index]

            # 2. Find the index of this exact dictionary in the ORIGINAL, UNSORTED list (tasks)
            # We must use the original list index to modify it in memory
            original_index = tasks.index(task_to_mark)
            
            # Check if already done
            if tasks[original_index]['done']:
                print(f"⚠️ Task {task_index} is already marked as done.")
                return

            # 3. Mark the task as done in the original list
            tasks[original_index]['done'] = True
            save_tasks(tasks)
            print(f"🎉 Task {task_index} marked as done!")
        else:
            print("❌ Invalid task number. Please try again.")

    except ValueError:
        print("❌ Invalid input. Please enter a number for the task index.")
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_task(tasks, task_index):
    """Deletes a task from the list based on its index from the sorted view."""
    # Since tasks are displayed sorted, we must sort the list to find the correct index!
    sorted_tasks = sort_tasks_by_priority(tasks.copy())

    try:
        index = task_index - 1

        if 0 <= index < len(sorted_tasks):
            # 1. Find the unique task dictionary based on the sorted list
            task_to_delete = sorted_tasks[index]

            # 2. Find the index of this exact dictionary in the ORIGINAL, UNSORTED list (tasks)
            original_index = tasks.index(task_to_delete)
            
            # 3. Delete the task from the original list
            deleted_task_desc = tasks[original_index]['description']
            tasks.pop(original_index) 
            save_tasks(tasks)
            print(f"🗑️ Deleted task {task_index}: '{deleted_task_desc}'")
        else:
            print("❌ Invalid task number. Please try again.")

    except ValueError:
        print("❌ Invalid input. Please enter a number for the task index.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    """The main function containing the application loop and menu."""
    tasks = load_tasks() # Load tasks when the program starts

    print("Welcome to your CLI To-Do Manager!")

    # The main loop keeps the program running until the user quits
    while True:
        print("\nWhat would you like to do?")
        print("1. View To-Dos")
        print("2. Add New To-Do")
        print("3. Mark To-Do as Done")
        print("4. Delete To-Do")
        print("5. Quit")
        
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            view_tasks(tasks)

        elif choice == '2':
            # Get the task description and priority
            new_task = input("Enter the new task description: ")
            
            while True:
                priority = input("Enter priority (H/M/L/None): ").upper()
                if priority in ['H', 'HIGH', 'M', 'MEDIUM', 'L', 'LOW', 'NONE', '']:
                    # Standardize input for the function
                    if priority in ['H', 'M', 'L']:
                        priority = {'H': 'HIGH', 'M': 'MEDIUM', 'L': 'LOW'}.get(priority)
                    elif priority == '':
                        priority = 'NONE'
                    break
                else:
                    print("Invalid priority. Please use H, M, L, or None.")

            add_task(tasks, new_task, priority)

        elif choice == '3':
            view_tasks(tasks)
            if tasks:
                try:
                    task_num = int(input("Enter the number of the task to mark as DONE: "))
                    mark_task_done(tasks, task_num)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

        elif choice == '4':
            view_tasks(tasks)
            if tasks:
                try:
                    task_num = int(input("Enter the number of the task to DELETE: "))
                    delete_task(tasks, task_num)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

        elif choice == '5':
            print("\nGoodbye! All tasks saved.")
            break # Exit the while loop

        else:
            print("🚫 Invalid choice. Please enter a number between 1 and 5.")

# This ensures the main() function runs only when the script is executed directly
if __name__ == "__main__":
    main()
