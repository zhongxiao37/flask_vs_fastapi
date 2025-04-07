# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy the project files
COPY pyproject.toml .
COPY app.py .

# Install dependencies
RUN pip install --no-cache-dir "fastapi>=0.110.0" "uvicorn>=0.27.1"

# Expose the port the app runs on
EXPOSE 5050

# Command to run the application
CMD ["python", "app.py"] 