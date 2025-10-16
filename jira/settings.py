DEFAULT_ENDPOINTS = {
    "issues": {
        "data_path": "issues",
        "api_path": "rest/api/3/search/jql",
        "params": {
            "fields": "id,key,summary,issuetype,status,priority,assignee,reporter,project,created,updated,resolutiondate,duedate,resolution",
            "expand": "fields,changelog",
            "validateQuery": "strict",
            "jql": "updated >= -90d",
        }
    },
    "users": {
        "api_path": "rest/api/3/users",
        "params": {
            "includeInactiveUsers": True,
            "fields": "accountId,displayName,emailAddress,active,timeZone"
        },
    },
    "projects": {
        "data_path": "values",
        "api_path": "rest/api/3/project/search",
        "params": {
            "status": "live,archived,deleted",
            "fields": "id,key,name,description,lead,projectTypeKey",
            "expand": "description,lead"
        },
    },
}

DEFAULT_PAGE_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY = 1.0
RATE_LIMIT_DELAY = 0.1
BATCH_SIZE = 50

MIN_ISSUE_AGE_HOURS = 1
MAX_ISSUES_PER_RUN = 10000