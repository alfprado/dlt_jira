{{
    config(
        materialized='table',
        unique_key='project_key',
        on_schema_change='append_new_columns'
    )
}}

WITH project_issues AS (
    SELECT 
        project_id,
        COUNT(DISTINCT issue_id) AS total_issues,
        COUNT(DISTINCT CASE WHEN status_category = 'Itens concluídos' THEN issue_id END) AS completed_issues,
        MIN(created_date) AS first_issue_date,
        MAX(updated_date) AS last_issue_update
    FROM 
        {{ ref('stg_jira_issues') }}
    GROUP BY 
        project_id
),

project_snapshot AS (
    SELECT 
        p.project_id,
        p.project_key,
        p.project_name,
        p.description,
        p.project_lead_id,
        p.project_lead_name,
        p.project_type_key,
        p.api_issue_count,
        p.last_issue_update_time,
        u.display_name AS lead_display_name,
        u.email_address AS lead_email,
        COALESCE(pi.total_issues, 0) AS actual_issue_count,
        COALESCE(pi.completed_issues, 0) AS completed_issues,
        CASE 
            WHEN COALESCE(pi.total_issues, 0) = 0 THEN 0::numeric
            ELSE (COALESCE(pi.completed_issues, 0)::numeric / COALESCE(pi.total_issues, 1)::numeric * 100)
        END AS completion_percentage,
        pi.first_issue_date,
        COALESCE(pi.last_issue_update, p.last_issue_update_time::timestamp) AS last_issue_update,
        CASE
            WHEN COALESCE(pi.total_issues, 0) = 0 THEN 'New'
            WHEN (COALESCE(pi.completed_issues, 0)::numeric / NULLIF(COALESCE(pi.total_issues, 1), 0)::numeric) >= 0.9 THEN 'Completed'
            WHEN (COALESCE(pi.completed_issues, 0)::numeric / NULLIF(COALESCE(pi.total_issues, 1), 0)::numeric) >= 0.5 THEN 'In Progress'
            ELSE 'Active'
        END AS project_status,
        CURRENT_TIMESTAMP AS valid_from_dttm,
        CURRENT_TIMESTAMP AS updated_dttm
    FROM 
        {{ ref('stg_jira_projects') }} p
    LEFT JOIN 
        project_issues pi ON p.project_id = pi.project_id
    LEFT JOIN
        {{ ref('stg_jira_users') }} u ON p.project_lead_id = u.account_id
)

SELECT 
    -- SCD Keys
    project_key,
    project_id,
    
    -- Business Keys
    project_name,
    project_lead_id,
    project_lead_name,
    
    -- Attributes
    description,
    project_type_key,
    api_issue_count,
    actual_issue_count AS total_issues,
    completed_issues,
    completion_percentage,
    first_issue_date,
    last_issue_update,
    project_status AS project_status_category,
    project_lead_name AS project_lead,
    lead_display_name,
    lead_email,
    
    -- SCD Type 1 Fields
    TRUE AS is_current,
    valid_from_dttm,
    NULL::timestamp AS valid_to_dttm,
    updated_dttm,
    
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'SCD_TYPE_1' AS scd_type

FROM project_snapshot