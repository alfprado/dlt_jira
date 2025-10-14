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
