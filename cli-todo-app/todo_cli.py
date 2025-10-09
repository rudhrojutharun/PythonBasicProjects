import os # We use this to get the current working directory for the task file

# --- CONFIGURATION ---
# The name of the file where tasks will be saved.
TASK_FILE = "todos.txt" 
# Prefix for completed tasks.
DONE_MARKER = "[x]"
# Prefix for incomplete tasks.
PENDING_MARKER = "[!]"

def load_tasks():
    """Loads tasks from the TASK_FILE, returning a list of task strings."""
    try:
        # 'r' mode means read-only.
        with open(TASK_FILE, 'r') as f:
            # .strip() removes any leading/trailing whitespace (like newlines)
            tasks = [line.strip() for line in f.readlines()]
        return tasks
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty list.
        return []

def save_tasks(tasks):
    """Saves the current list of tasks to the TASK_FILE."""
    # 'w' mode means write-mode. It overwrites the file completely.
    with open(TASK_FILE, 'w') as f:
        for task in tasks:
            # Write each task followed by a newline character
            f.write(f"{task}\n")

def view_tasks(tasks):
    """Displays the list of tasks with their index."""
    if not tasks:
        print("\n--- Your To-Do List is Empty! ---\n")
        return

    print("\n==================================")
    print("        CURRENT TO-DO LIST        ")
    print("==================================")
    
    # Enumerate provides both the index (starting at 0) and the item.
    for index, task in enumerate(tasks):
        # We display the index starting at 1 for the user (index + 1)
        print(f"{index + 1}. {task}")
    
    print("==================================\n")

def add_task(tasks, new_task_desc):
    """Adds a new task to the list with the PENDING_MARKER."""
    if new_task_desc.strip():
        # A new task is always pending by default
        tasks.append(f"{PENDING_MARKER} {new_task_desc.strip()}")
        save_tasks(tasks)
        print(f"✅ Added task: '{new_task_desc.strip()}'")
    else:
        print("❌ Task description cannot be empty.")

def mark_task_done(tasks, task_index):
    """Marks a task as complete by replacing the PENDING_MARKER with the DONE_MARKER."""
    try:
        # Convert index (which starts from 1 for the user) to list index (0-based)
        index = task_index - 1
        
        # Check if the index is valid
        if 0 <= index < len(tasks):
            task = tasks[index]
            
            # Check if the task is already done
            if task.startswith(DONE_MARKER):
                print(f"⚠️ Task {task_index} is already marked as done.")
                return

            # Replace the PENDING_MARKER with the DONE_MARKER
            tasks[index] = task.replace(PENDING_MARKER, DONE_MARKER, 1)
            save_tasks(tasks)
            print(f"🎉 Task {task_index} marked as done!")
        else:
            print("❌ Invalid task number. Please try again.")

    except ValueError:
        print("❌ Invalid input. Please enter a number for the task index.")
    except Exception as e:
        print(f"An error occurred: {e}")


def delete_task(tasks, task_index):
    """Deletes a task from the list based on its index."""
    try:
        # Convert index (which starts from 1 for the user) to list index (0-based)
        index = task_index - 1

        # Check if the index is valid
        if 0 <= index < len(tasks):
            deleted_task = tasks.pop(index) # .pop removes and returns the item
            save_tasks(tasks)
            print(f"🗑️ Deleted task {task_index}: '{deleted_task.strip()}'")
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
            # Get the task description from the user
            new_task = input("Enter the new task description: ")
            add_task(tasks, new_task)

        elif choice == '3':
            view_tasks(tasks)
            if tasks:
                # Ask the user for the task number to mark as done
                try:
                    task_num = int(input("Enter the number of the task to mark as DONE: "))
                    mark_task_done(tasks, task_num)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

        elif choice == '4':
            view_tasks(tasks)
            if tasks:
                # Ask the user for the task number to delete
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
