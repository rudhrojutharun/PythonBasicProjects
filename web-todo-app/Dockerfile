# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the PORT environment variable required by Cloud Run
ENV PORT 8080

# Command to run the application using Gunicorn (production web server)
# This command tells Gunicorn to look inside the 'todo_web_service' file
# and find the Flask instance named 'app'.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 todo_web_service:app
