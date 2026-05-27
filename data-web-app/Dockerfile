# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p /app/data/csv /app/data/uploads /app/static

# Set default environment variables
ENV APP_NAME="Data Web Application" \
    APP_VERSION="1.0.0" \
    DATA_SOURCE="csv" \
    CSV_DIRECTORY="/app/data/csv" \
    UPLOAD_DIRECTORY="/app/data/uploads" \
    DB_HOST="postgres" \
    DB_PORT="5432" \
    DB_NAME="data_app" \
    DB_USER="postgres" \
    DB_PASSWORD="postgres"

# Expose port
EXPOSE 8000

# Set default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# For production, use gunicorn
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
