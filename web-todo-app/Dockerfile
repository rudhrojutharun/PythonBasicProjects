# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Install gunicorn along with app dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the PORT environment variable required by Cloud Run (default 8080)
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Command to run the application using Gunicorn. 
# We explicitly bind to 0.0.0.0 (all IPs) on the required port.
# Gunicorn will start the app instance found in todo_web_service.py
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 todo_web_service:app
