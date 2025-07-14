FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/processed /app/models /opt/dagster/dagster_home

# Download YOLO model
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Set environment variables
ENV PYTHONPATH=/app
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Expose ports
EXPOSE 8000 3000

# Default command
CMD ["python", "-m", "uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"] 