#!/bin/sh

# Atualizar secrets.toml com as variáveis de ambiente
cat > /app/.dlt/secrets.toml << EOF
[sources.jira]
subdomain = "${JIRA_SUBDOMAIN}"
email = "${JIRA_EMAIL}"
api_token = "${JIRA_API_TOKEN}"

# PostgreSQL Configuration
[destination.postgres.credentials]
database = "${POSTGRES_DB}"
password = "${POSTGRES_PASSWORD}"
username = "${POSTGRES_USER}"
host = "postgres"
port = ${POSTGRES_PORT}
connect_timeout = 15
EOF

# Export environment variables for DBT
export POSTGRES_HOST="${POSTGRES_HOST}"
export POSTGRES_PORT="${POSTGRES_PORT}"
export POSTGRES_USER="${POSTGRES_USER}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
export POSTGRES_DB="${POSTGRES_DB}"

# Execute pipeline with provided argument or 'all' by default
# Handle docker compose run pattern: python jira_pipeline.py <arg>
if [ "$1" = "python" ] && [ "$2" = "jira_pipeline.py" ]; then
    PIPELINE_ARG=${3:-all}
else
    PIPELINE_ARG=${1:-all}
fi

echo "🚀 Running pipeline with argument: $PIPELINE_ARG"
python jira_pipeline.py $PIPELINE_ARG