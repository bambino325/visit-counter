# Use a lightweight Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent directly to the terminal
ENV PYTHONUNBUFFERED=1

# Copy dependencies first
COPY requirements.txt .

# Install application dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Create a non-root user
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Document the application port
EXPOSE 5000

# Start the application using Gunicorn
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${APP_PORT:-5000} app.main:app"]
