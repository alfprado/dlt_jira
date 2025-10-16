# Configurações otimizadas para ingestão Jira
# Seguindo boas práticas de mercado

# Define endpoints
DEFAULT_ENDPOINTS = {
    "issues": {
        "data_path": "issues",
        "api_path": "jql",
        "params": {
            "fields": "*all",
            "expand": "fields,changelog,operations,transitions,names",
            "validateQuery": "strict",
            "jql": "updated >= -90d",
        }
    },
    "users": {
        "api_path": "rest/api/3/users",
        "params": {"includeInactiveUsers": True},
    },
    "workflows": {
        "data_path": "values",
        "api_path": "/rest/api/3/workflow/search",
        "params": {},
    },
    "projects": {
        "data_path": "values",
        "api_path": "rest/api/3/project/search",
        "params": {
            "status": "live,archived,deleted",
            "expand": "description,lead,issueTypes,url,projectKeys,permissions,insight"
        },
    },
}

DEFAULT_PAGE_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # segundos
RATE_LIMIT_DELAY = 0.1  # 100ms entre requests
BATCH_SIZE = 50  # Para processamento em lotes

# Configurações de qualidade de dados
MIN_ISSUE_AGE_HOURS = 1  # Issues mais recentes que 1 hora
MAX_ISSUES_PER_RUN = 10000  # Limite de segurança