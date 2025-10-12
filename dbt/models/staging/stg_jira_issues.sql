{{
    config(
        materialized='view'
    )
}}

SELECT 
    -- Primary keys
    id AS issue_id,
    key AS issue_key,
    
    -- Basic issue information
    fields__summary AS summary,
    fields__issuetype__name AS issue_type,
    fields__issuetype__id AS issue_type_id,
    
    -- Status information
    fields__status__name AS status,
    fields__status__id AS status_id,
    fields__status__status_category__name AS status_category,
    
    -- Priority information
    fields__priority__name AS priority,
    fields__priority__id AS priority_id,
    
    -- Assignee information
    fields__assignee__account_id AS assignee_id,
    fields__assignee__display_name AS assignee_name,
    fields__assignee__email_address AS assignee_email,
    
    -- Reporter information
    fields__reporter__account_id AS reporter_id,
    fields__reporter__display_name AS reporter_name,
    fields__reporter__email_address AS reporter_email,
    
    -- Project information
    fields__project__id AS project_id,
    fields__project__key AS project_key,
    fields__project__name AS project_name,
    
    -- Important dates (converted to timestamp)
    fields__created::timestamp AS created_date,
    fields__updated::timestamp AS updated_date,
    fields__resolutiondate::timestamp AS resolution_date,
    fields__duedate::timestamp AS due_date,
    
    -- Resolution information
    fields__resolution__name AS resolution,
    
    -- Labels and components (as arrays) - commented out as fields may not exist
    -- fields__labels AS labels,
    -- fields__components AS components,
    
    -- Time tracking (if available) - commented out as fields may not exist
    -- fields__timeoriginalestimate AS original_estimate_seconds,
    -- fields__timespent AS time_spent_seconds,
    
    -- Additional metadata
    _dlt_id

FROM 
    {{ source('jira_data', 'issues') }}
