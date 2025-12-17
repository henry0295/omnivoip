# =============================================================================
# OmniVoIP Backend (Django) Dockerfile
# =============================================================================

FROM python:3.11-slim as base

LABEL maintainer="henry0295"
LABEL description="OmniVoIP Contact Center Backend"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql-client \
    gettext \
    curl \
    libssl-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs && \
    chmod -R 755 /app/media /app/static /app/logs

# Copy and set entrypoint
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN useradd -m -u 1000 omnivoip && \
    chown -R omnivoip:omnivoip /app

USER omnivoip

# Expose port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "omnivoip.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
