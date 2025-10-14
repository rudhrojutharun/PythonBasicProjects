from flask import Flask, render_template_string, request, jsonify
from firebase_admin import initialize_app, firestore, credentials, auth
from functools import wraps
import json
import os

# --- CONFIGURATION CONSTANTS ---
FIREBASE_KEY_FILE = "serviceAccountKey.json"
FIREBASE_READY = False
TASKS_COLLECTION = None

# --- 1. FIREBASE CONFIGURATION & INITIALIZATION ---

def initialize_firebase():
    """Initializes Firebase using local key (for dev) or env vars (for deploy)."""
    global FIREBASE_READY, TASKS_COLLECTION, db

    # 1. Attempt to load local service account key
    if os.path.exists(FIREBASE_KEY_FILE):
        try:
            print(f"Attempting local connection using {FIREBASE_KEY_FILE}...")
            
            with open(FIREBASE_KEY_FILE, 'r') as f:
                key_data = json.load(f)
                project_id = key_data['project_id']

            cred = credentials.Certificate(FIREBASE_KEY_FILE)
            initialize_app(cred)
            db = firestore.client()
            
            TASKS_COLLECTION = db.collection(f'artifacts/{project_id}/public/data/tasks')
            
            FIREBASE_READY = True
            print("✅ Successfully connected to Firestore using local service account.")
            return

        except Exception as e:
            print(f"!!! ERROR: Local key found but failed to connect. Ensure key is valid. Error: {e}")

    # 2. Attempt to load environment variables (for deployed environments)
    app_id = os.environ.get('__app_id')
    firebase_config_json = os.environ.get('__firebase_config')

    if app_id and firebase_config_json:
        try:
            print("Attempting connection using deployment environment variables...")
            firebase_config = json.loads(firebase_config_json)
            
            cred = credentials.Certificate(firebase_config)
            initialize_app(cred)
            db = firestore.client()
            
            TASKS_COLLECTION = db.collection(f'artifacts/{app_id}/public/data/tasks')
            FIREBASE_READY = True
            print("✅ Successfully connected to Firestore using deployment variables.")
            return

        except Exception as e:
            print(f"!!! ERROR: Deployment configuration found but failed. Error: {e}")
            
    # 3. Fallback: If neither method worked, run in disabled mode
    print("!!! WARNING: FIREBASE IS NOT CONNECTED. Tasks will not be saved.")
    FIREBASE_READY = False

initialize_firebase()
    
# --- APPLICATION SETUP ---
app = Flask(__name__)

# --- DECORATOR FOR AUTHENTICATION ---
# This decorator will protect our routes
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the ID token from the Authorization header
        id_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        if not id_token:
            return jsonify({'message': 'Authorization token is missing!'}), 403

        try:
            # Verify the ID token using the Firebase Admin SDK
            decoded_token = auth.verify_id_token(id_token)
            # Add the user's UID to the request object for use in the route
            request.user_id = decoded_token['uid']
        except auth.AuthError as e:
            return jsonify({'message': f'Token is invalid or expired: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# --- HTML TEMPLATE (With Auth Forms) ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web To-Do App (Firestore)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        .task-done { text-decoration: line-through; color: #6b7280; }
        .priority-high { color: #dc2626; font-weight: 700; }
        .priority-medium { color: #fbbf24; font-weight: 600; }
        .priority-low { color: #10b981; }
    </style>
    <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-auth.js"></script>
</head>
<body class="p-8">

    <div id="auth-container" class="max-w-md mx-auto bg-white p-6 rounded-xl shadow-2xl">
        <h2 class="text-2xl font-bold text-center mb-4 text-gray-800">Sign Up / Log In</h2>
        <div class="space-y-4">
            <input type="email" id="email" placeholder="Email" required class="w-full p-3 border rounded-lg">
            <input type="password" id="password" placeholder="Password" required class="w-full p-3 border rounded-lg">
            <div class="flex gap-4">
                <button onclick="handleAuth(true)" class="flex-grow bg-green-500 text-white p-3 rounded-lg font-semibold hover:bg-green-600 transition">Sign Up</button>
                <button onclick="handleAuth(false)" class="flex-grow bg-indigo-600 text-white p-3 rounded-lg font-semibold hover:bg-indigo-700 transition">Log In</button>
            </div>
            <p class="text-center text-xs text-gray-500">Your data will be stored separately based on your account.</p>
        </div>
    </div>

    <div id="app-container" class="max-w-xl mx-auto bg-white p-6 rounded-xl shadow-2xl hidden">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">🚀 Your To-Do Manager</h1>
        <button onclick="authService.signOut()" class="absolute top-8 right-8 text-sm text-red-500 hover:text-red-700 font-semibold">Log Out</button>

        <p id="auth-status" class="text-center text-sm mb-4">
            You are signed in. 
        </p>

        <form id="add-task-form" class="flex mb-8 gap-3" onsubmit="event.preventDefault(); submitTask();">
            <input type="text" id="description" name="description" placeholder="New task description..." required
                   class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 transition duration-150 shadow-sm">
            <select id="priority" name="priority" 
                    class="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 shadow-sm w-32">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
            </select>
            <button type="submit"
                    class="bg-indigo-600 text-white p-3 rounded-lg font-semibold hover:bg-indigo-700 transition duration-150 shadow-md hover:shadow-lg">
                Add Task
            </button>
        </form>

        <ul id="task-list-placeholder" class="space-y-3"></ul>
    </div>
    
    <script>
        // Your Firebase client-side config 
        var firebaseConfig = {
            apiKey: "{{ FIREBASE_CONFIG.get('apiKey') }}",
            authDomain: "{{ FIREBASE_CONFIG.get('authDomain') }}",
            projectId: "{{ FIREBASE_CONFIG.get('projectId') }}",
            storageBucket: "{{ FIREBASE_CONFIG.get('storageBucket') }}",
            messagingSenderId: "{{ FIREBASE_CONFIG.get('messagingSenderId') }}",
            appId: "{{ FIREBASE_CONFIG.get('appId') }}"
        };
        firebase.initializeApp(firebaseConfig);
        const authService = firebase.auth();

        // Main auth listener
        authService.onAuthStateChanged(user => {
            if (user) {
                document.getElementById('auth-container').classList.add('hidden');
                document.getElementById('app-container').classList.remove('hidden');
                
                user.getIdToken().then(idToken => {
                    fetchTasks(idToken);
                }).catch(error => {
                    console.error("Failed to get ID token:", error);
                });

            } else {
                document.getElementById('auth-container').classList.remove('hidden');
                document.getElementById('app-container').classList.add('hidden');
                document.getElementById('task-list-placeholder').innerHTML = '';
            }
        });

        function fetchTasks(idToken) {
            fetch('/get_tasks', { 
                headers: { 'Authorization': 'Bearer ' + idToken }
            }).then(response => {
                if (!response.ok) {
                    // If Flask returns 401/403 (expired/invalid token), force sign out
                    if (response.status === 401 || response.status === 403) {
                         authService.signOut();
                         alert("Session expired. Please log in again.");
                    }
                    throw new Error('Failed to fetch tasks: ' + response.statusText);
                }
                return response.json();
            })
              .then(data => {
                  const tasksList = document.getElementById('task-list-placeholder');
                  tasksList.innerHTML = '';
                  data.tasks.forEach(task => {
                      const li = document.createElement('li');
                      li.className = "flex items-center justify-between bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm transition duration-150 hover:bg-gray-100 relative";
                      
                      let priorityClass = '';
                      if (task.priority === 'HIGH') priorityClass = 'priority-high';
                      if (task.priority === 'MEDIUM') priorityClass = 'priority-medium';
                      if (task.priority === 'LOW') priorityClass = 'priority-low';
                      
                      const doneClass = task.done ? 'task-done' : 'text-gray-800';

                      let buttonsHtml = '';
                      if (!task.done) {
                          buttonsHtml += `<button onclick="markDone('${task.id}')" title="Mark Done"
                                            class="bg-green-500 text-white p-2 rounded-full hover:bg-green-600 transition duration-150 shadow-sm">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                            </svg>
                                        </button>`;
                      }
                      buttonsHtml += `<button onclick="deleteTask('${task.id}')" title="Delete"
                                        class="bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition duration-150 shadow-sm">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                                        </svg>
                                    </button>`;

                      li.innerHTML = `
                          <div class="flex items-center flex-grow">
                              <span class="text-sm mr-4 text-gray-500 border-r pr-4 ${priorityClass}">
                                  ${task.priority}
                              </span>
                              <span class="text-lg ${doneClass}">
                                  ${task.description}
                              </span>
                          </div>
                          <div class="flex space-x-2 ml-4">
                              ${buttonsHtml}
                          </div>
                      `;
                      tasksList.appendChild(li);
                  });
              })
              .catch(error => console.error('Error fetching tasks:', error));
        }

        function handleAuth(isSignUp) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            if (!email || !password) {
                alert("Please enter both email and password.");
                return;
            }

            if (isSignUp) {
                authService.createUserWithEmailAndPassword(email, password)
                    .then(() => { alert("Account created! You can now log in."); })
                    .catch(error => { alert("Sign Up Error: " + error.message); });
            } else {
                authService.signInWithEmailAndPassword(email, password)
                    .then(() => { console.log("Signed in successfully!"); })
                    .catch(error => { alert("Sign In Error: " + error.message); });
            }
        }
        
        function submitTask() {
            const description = document.getElementById('description').value;
            const priority = document.getElementById('priority').value;
            authService.currentUser.getIdToken().then(idToken => {
                fetch('/add', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json', 
                        'Authorization': 'Bearer ' + idToken 
                    },
                    body: JSON.stringify({ description, priority })
                }).then(response => {
                    if (!response.ok) {
                         // Check for errors like 401/403 from the server
                         throw new Error('Failed to add task: ' + response.statusText);
                    }
                    return authService.currentUser.getIdToken();
                }).then(newToken => fetchTasks(newToken)); // Re-fetch tasks after adding
            }).catch(error => {
                console.error("Task Submission Error:", error);
                alert("Error submitting task. Check console.");
            });
            document.getElementById('description').value = ''; // Clear input field
        }
        
        function markDone(taskId) {
            authService.currentUser.getIdToken().then(idToken => {
                fetch(`/done/${taskId}`, {
                    method: 'POST',
                    headers: { 'Authorization': 'Bearer ' + idToken }
                }).then(() => fetchTasks(idToken));
            });
        }
        
        function deleteTask(taskId) {
            authService.currentUser.getIdToken().then(idToken => {
                fetch(`/delete/${taskId}`, {
                    method: 'POST',
                    headers: { 'Authorization': 'Bearer ' + idToken }
                }).then(() => fetchTasks(idToken));
            });
        }
    </script>
</body>
</html>
"""

# --- FLASK ROUTES ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main page. The client-side JS handles fetching the tasks."""
    # We now fetch the Firebase client config and pass it to the template
    firebase_config = {
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID')
    }
    return render_template_string(HTML_TEMPLATE, FIREBASE_CONFIG=firebase_config)

@app.route('/get_tasks', methods=['GET'])
@token_required
def get_tasks():
    """Fetches tasks for the logged-in user and returns them as JSON."""
    tasks = []
    if FIREBASE_READY:
        try:
            # Query the database for tasks belonging to the current user
            tasks_stream = TASKS_COLLECTION.where('user_id', '==', request.user_id).stream()
            for doc in tasks_stream:
                task = doc.to_dict()
                task['id'] = doc.id
                tasks.append(task)
            
            # Sort logic remains the same
            priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            tasks.sort(key=lambda t: (
                t.get('done', False), 
                priority_order.get(t.get('priority', 'LOW').upper(), 4)
            ))
            
        except Exception as e:
            print(f"Firestore Read Error: {e}")
            
    return jsonify(tasks=tasks)

@app.route('/add', methods=['POST'])
@token_required
def add_task():
    """Handles adding a new task to Firestore for the authenticated user."""
    if FIREBASE_READY:
        data = request.get_json()
        description = data.get('description')
        priority = data.get('priority').upper()
        
        if description and priority:
            new_task = {
                'user_id': request.user_id, # Store the user's ID with the task
                'description': description,
                'done': False,
                'priority': priority
            }
            TASKS_COLLECTION.add(new_task)
    return jsonify(success=True)

@app.route('/done/<task_id>', methods=['POST'])
@token_required
def mark_done(task_id):
    """Handles marking a task as done in Firestore for the authenticated user."""
    if FIREBASE_READY:
        try:
            task_ref = TASKS_COLLECTION.document(task_id)
            # Security check: Ensure the task belongs to the user
            task_data = task_ref.get().to_dict()
            if task_data and task_data.get('user_id') == request.user_id:
                task_ref.update({'done': True})
        except Exception as e:
            print(f"Firestore Update Error (Mark Done): {e}")
            
    return jsonify(success=True)

@app.route('/delete/<task_id>', methods=['POST'])
@token_required
def delete_task(task_id):
    """Handles deleting a task from Firestore for the authenticated user."""
    if FIREBASE_READY:
        try:
            task_ref = TASKS_COLLECTION.document(task_id)
            # Security check: Ensure the task belongs to the user
            task_data = task_ref.get().to_dict()
            if task_data and task_data.get('user_id') == request.user_id:
                task_ref.delete()
        except Exception as e:
            print(f"Firestore Delete Error: {e}")

    return jsonify(success=True)

# --- SERVER STARTUP ---
if __name__ == '__main__':
    app.run(debug=True)
