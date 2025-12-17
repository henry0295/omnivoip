FROM python:3.11-slim

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="OmniVoIP Dialer Worker - Celery"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 celery && \
    chown -R celery:celery /app

USER celery

# Run Celery worker
CMD ["celery", "-A", "tasks", "worker", \
     "--loglevel=info", \
     "--concurrency=4", \
     "--max-tasks-per-child=1000"]
