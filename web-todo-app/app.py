from flask import Flask, render_template_string, request, redirect, url_for
from firebase_admin import initialize_app, firestore, credentials
import json
import os

# --- 1. FIREBASE CONFIGURATION & INITIALIZATION ---

# Global variables for Canvas environment.
# We must ensure they exist before trying to use them.
try:
    app_id = os.environ.get('__app_id', 'default-app-id')
    firebase_config = json.loads(os.environ.get('__firebase_config'))
    
    # Initialize the Firebase Admin SDK using credentials from the config
    # Note: Flask runs as a server, so we use the Admin SDK, not the client SDK.
    cred = credentials.Certificate(firebase_config)
    initialize_app(cred)
    db = firestore.client()
    
    # Define the Firestore collection path (Public data for the app)
    TASKS_COLLECTION = db.collection(f'artifacts/{app_id}/public/data/tasks')
    FIREBASE_READY = True
except Exception as e:
    # If initialization fails (e.g., if running outside the Canvas environment)
    print(f"!!! WARNING: FIREBASE INITIALIZATION FAILED: {e}")
    FIREBASE_READY = False
    
# --- APPLICATION SETUP ---
app = Flask(__name__)

# --- HTML TEMPLATE (Frontend unchanged) ---
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
        .priority-high { color: #dc2626; font-weight: 700; }
        .priority-medium { color: #fbbf24; font-weight: 600; }
        .priority-low { color: #10b981; }
    </style>
</head>
<body class="p-8">
    <div class="max-w-xl mx-auto bg-white p-6 rounded-xl shadow-2xl">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">🚀 Web To-Do Manager (Firestore)</h1>
        
        {% if not FIREBASE_READY %}
        <p class="text-center text-sm text-red-600 mb-6 font-bold bg-red-100 p-2 rounded-lg">
            🚨 WARNING: Firestore is NOT connected. Tasks are disabled.
        </p>
        {% endif %}
        
        <!-- Add New Task Form -->
        <form method="POST" action="{{ url_for('add_task') }}" class="flex mb-8 gap-3">
            <input type="text" name="description" placeholder="New task description..." required
                   class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 transition duration-150 shadow-sm">
            <select name="priority" 
                    class="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 shadow-sm w-32">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
            </select>
            <button type="submit" {% if not FIREBASE_READY %}disabled{% endif %}
                    class="bg-indigo-600 text-white p-3 rounded-lg font-semibold hover:bg-indigo-700 transition duration-150 shadow-md hover:shadow-lg disabled:opacity-50">
                Add Task
            </button>
        </form>

        <!-- To-Do List Display -->
        <ul class="space-y-3">
            {% for task in tasks %}
            <li class="flex items-center justify-between bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm transition duration-150 hover:bg-gray-100">
                <!-- Task Status & Priority -->
                <div class="flex items-center flex-grow">
                    <span class="text-sm mr-4 text-gray-500 border-r pr-4 
                        {% if task.priority == 'HIGH' %}priority-high
                        {% elif task.priority == 'MEDIUM' %}priority-medium
                        {% elif task.priority == 'LOW' %}priority-low
                        {% endif %}">
                        {{ task.priority }}
                    </span>
                    <!-- Task Description -->
                    <span class="text-lg {{ 'task-done' if task.done else 'text-gray-800' }}">
                        {{ task.description }}
                    </span>
                </div>

                <!-- Action Buttons -->
                <div class="flex space-x-2 ml-4">
                    {% if not task.done %}
                        <!-- Mark Done Button -->
                        <form method="POST" action="{{ url_for('mark_done', task_id=task.id) }}">
                            <button type="submit" title="Mark Done" {% if not FIREBASE_READY %}disabled{% endif %}
                                    class="bg-green-500 text-white p-2 rounded-full hover:bg-green-600 transition duration-150 shadow-sm disabled:opacity-50">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </form>
                    {% endif %}

                    <!-- Delete Button -->
                    <form method="POST" action="{{ url_for('delete_task', task_id=task.id) }}">
                        <button type="submit" title="Delete" {% if not FIREBASE_READY %}disabled{% endif %}
                                class="bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition duration-150 shadow-sm disabled:opacity-50">
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
    """Fetches tasks from Firestore and renders the main page."""
    tasks = []
    if FIREBASE_READY:
        try:
            # Fetch all documents (tasks) from the collection
            tasks_stream = TASKS_COLLECTION.stream()
            for doc in tasks_stream:
                task = doc.to_dict()
                task['id'] = doc.id  # Store the Firestore document ID for operations
                tasks.append(task)
                
            # Sort by 'done' status first (done tasks go to the bottom)
            # Then sort by priority (HIGH=1, MEDIUM=2, LOW=3)
            priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            tasks.sort(key=lambda t: (t.get('done', False), priority_order.get(t.get('priority', 'LOW').upper(), 4)))
            
        except Exception as e:
            print(f"Firestore Read Error: {e}")
            
    return render_template_string(HTML_TEMPLATE, tasks=tasks, FIREBASE_READY=FIREBASE_READY)

@app.route('/add', methods=['POST'])
def add_task():
    """Handles adding a new task to Firestore."""
    if FIREBASE_READY:
        description = request.form.get('description')
        priority = request.form.get('priority').upper()
        
        if description and priority:
            new_task = {
                'description': description,
                'done': False,
                'priority': priority
            }
            # Add the document to the collection, letting Firestore generate the ID
            TASKS_COLLECTION.add(new_task)
    return redirect(url_for('index'))

@app.route('/done/<task_id>', methods=['POST'])
def mark_done(task_id):
    """Handles marking a task as done in Firestore."""
    if FIREBASE_READY:
        # Get a reference to the specific document using the task_id (which is the Firestore document ID)
        task_ref = TASKS_COLLECTION.document(task_id)
        
        # Update the 'done' field
        task_ref.update({'done': True})
    return redirect(url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    """Handles deleting a task from Firestore."""
    if FIREBASE_READY:
        # Delete the specific document
        TASKS_COLLECTION.document(task_id).delete()
    return redirect(url_for('index'))

# --- SERVER STARTUP ---
if __name__ == '__main__':
    # Flask runs the application in debug mode which is useful for development
    app.run(debug=True)
