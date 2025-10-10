from flask import Flask, render_template_string, request, redirect, url_for
import os

# --- APPLICATION SETUP ---
app = Flask(__name__)

# Mock database (in-memory storage) for initial testing. 
# We will replace this with Firestore later.
tasks = [
    {'id': 't1', 'description': 'Set up Firestore connection (HIGH)', 'done': False},
    {'id': 't2', 'description': 'Design basic HTML layout (MEDIUM)', 'done': False},
    {'id': 't3', 'description': 'Convert CLI logic to web routes (LOW)', 'done': False},
]

# --- HTML TEMPLATE (This is the entire single-page frontend) ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web To-Do App</title>
    <!-- Load Tailwind CSS for styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        .task-done { text-decoration: line-through; color: #6b7280; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-xl mx-auto bg-white p-6 rounded-xl shadow-2xl">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">🚀 Web To-Do Manager</h1>
        <p class="text-center text-sm text-red-500 mb-6">
            Currently using IN-MEMORY storage. Tasks will disappear when the server restarts.
        </p>
        
        <!-- Add New Task Form -->
        <form method="POST" action="{{ url_for('add_task') }}" class="flex mb-8 gap-3">
            <input type="text" name="description" placeholder="New task description..." required
                   class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 transition duration-150 shadow-sm">
            <button type="submit"
                    class="bg-indigo-600 text-white p-3 rounded-lg font-semibold hover:bg-indigo-700 transition duration-150 shadow-md hover:shadow-lg">
                Add Task
            </button>
        </form>

        <!-- To-Do List Display -->
        <ul class="space-y-3">
            {% for task in tasks %}
            <li class="flex items-center justify-between bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm transition duration-150 hover:bg-gray-100">
                <!-- Task Description -->
                <span class="text-lg {{ 'task-done' if task.done else 'text-gray-800' }} flex-grow">
                    {{ task.description }}
                </span>

                <!-- Action Buttons -->
                <div class="flex space-x-2 ml-4">
                    {% if not task.done %}
                        <!-- Mark Done Button -->
                        <form method="POST" action="{{ url_for('mark_done', task_id=task.id) }}">
                            <button type="submit" title="Mark Done"
                                    class="bg-green-500 text-white p-2 rounded-full hover:bg-green-600 transition duration-150 shadow-sm">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </form>
                    {% endif %}

                    <!-- Delete Button -->
                    <form method="POST" action="{{ url_for('delete_task', task_id=task.id) }}">
                        <button type="submit" title="Delete"
                                class="bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition duration-150 shadow-sm">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </form>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# --- FLASK ROUTES ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main To-Do list page."""
    # Note: We sort here to ensure done tasks appear at the bottom
    sorted_tasks = sorted(tasks, key=lambda t: t['done'])
    return render_template_string(HTML_TEMPLATE, tasks=sorted_tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Handles adding a new task."""
    description = request.form.get('description')
    if description:
        # Create a simple unique ID (we will use Firestore's ID later)
        new_id = f"t{len(tasks) + 1}"
        new_task = {
            'id': new_id,
            'description': description,
            'done': False
        }
        tasks.append(new_task)
    return redirect(url_for('index'))

@app.route('/done/<task_id>', methods=['POST'])
def mark_done(task_id):
    """Handles marking a task as done."""
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = True
            break
    return redirect(url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    """Handles deleting a task."""
    global tasks
    # Rebuild the tasks list, excluding the one with the matching ID
    tasks = [task for task in tasks if task['id'] != task_id]
    return redirect(url_for('index'))

# --- SERVER STARTUP ---
if __name__ == '__main__':
    # Flask runs the application in debug mode which is useful for development
    app.run(debug=True)
