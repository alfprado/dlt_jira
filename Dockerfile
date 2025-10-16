# Simple and optimized Dockerfile for Jira data pipeline
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DBT_LOG_PATH="/tmp/dbt_logs"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY jira/ /app/jira/
COPY orchestrator.py /app/
COPY run_pipeline.py /app/
COPY monitor.py /app/
COPY .dlt/ /app/.dlt/
COPY dbt/ /app/dbt/

# Create directories
RUN mkdir -p /app/logs /tmp/dbt_logs

# Copy and setup entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import dlt, dbt; print('OK')" 2>/dev/null || exit 1

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []