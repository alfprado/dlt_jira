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
    
    -- Insight data (if available)
    NULL AS api_issue_count,
    NULL AS last_issue_update_time,
    
    -- Additional metadata
    _dlt_id

FROM 
    {% if var('load_projects', true) %}
        {{ source('jira_data', 'projects') }}
    {% else %}
        (SELECT NULL::text AS id, NULL::text AS key, NULL::text AS name, NULL::text AS description, NULL::text AS lead__account_id, NULL::text AS lead__display_name, NULL::text AS project_type_key, NULL::text AS _dlt_id WHERE 1=0) AS projects
    {% endif %}
