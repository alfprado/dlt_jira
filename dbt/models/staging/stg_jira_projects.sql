{{
    config(
        materialized='view'
    )
}}

SELECT 
    -- Primary key
    id AS project_id,
    
    -- Project information
    key AS project_key,
    name AS project_name,
    description,
    
    -- Project lead information
    lead__account_id AS project_lead_id,
    lead__display_name AS project_lead_name,
    
    -- Project metadata
    project_type_key,
    
    -- Insight data
    insight__total_issue_count AS api_issue_count,
    insight__last_issue_update_time AS last_issue_update_time,
    
    -- Additional metadata
    _dlt_id

FROM 
    {{ source('jira_data', 'projects') }}
