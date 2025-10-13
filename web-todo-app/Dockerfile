# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Flask runs on port 8080 by default on Cloud Run
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Command to run the application using Gunicorn (a production web server)
# Note: We must explicitly tell Flask/Gunicorn which file to run,
#       and we use the correct environment to enable live deployment.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 todo_web_service:app
