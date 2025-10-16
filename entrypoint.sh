#!/bin/bash
set -euo pipefail

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Create directories if they do not exist
mkdir -p /app/logs /tmp/dbt_logs

# Install dbt dependencies
log "Installing dbt dependencies..."
cd /app/dbt
if dbt deps --quiet; then
    log "dbt dependencies installed successfully"
else
    log "Error installing dbt dependencies"
    exit 1
fi

# Execute pipeline or direct command
log "Starting pipeline..."
cd /app
if [ "${1:-}" = "python" ] && [ "${2:-}" = "-c" ]; then
    exec "$@"
else
    exec python run_pipeline.py "$@"
fi
