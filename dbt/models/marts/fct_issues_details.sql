{{
    config(
        materialized='table',
        unique_key='issue_key',
        on_schema_change='append_new_columns'
    )
}}

WITH issue_changelog AS (
    SELECT
        issue_dlt_id,
        COUNT(DISTINCT history_id) AS change_count,
        COUNT(DISTINCT CASE WHEN field = 'status' THEN history_id END) AS status_change_count,
        COUNT(DISTINCT CASE WHEN field = 'assignee' THEN history_id END) AS assignee_change_count,
        MIN(change_date) AS first_change_date,
        MAX(change_date) AS last_change_date
    FROM
        {{ ref('stg_jira_changelog') }}
    GROUP BY
        issue_dlt_id
)

SELECT 
    -- Primary Keys
    i.issue_key,
    i.issue_id,
    
    -- Business Keys
    i.issue_type,
    i.status,
    i.priority,
    i.project_id,
    i.assignee_id,
    i.reporter_id,
    
    -- Descriptive Attributes
    i.summary,
    i.status_category,
    i.resolution,
    
    -- Denormalized Fields for Dashboard Compatibility
    u.display_name AS assignee_name,
    r.display_name AS reporter_name,
    p.project_name,
    
    -- Foreign Keys to Dimensions (already included above)
    
    -- Dates
    i.created_date,
    i.updated_date,
    i.resolution_date,
    i.due_date,
    
    -- Calculated Metrics
    CASE 
        WHEN i.resolution_date IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (i.resolution_date - i.created_date))/86400 
        ELSE NULL 
    END AS days_to_resolution,
    
    CASE 
        WHEN i.updated_date > i.created_date
        THEN EXTRACT(EPOCH FROM (i.updated_date - i.created_date))/86400 
        ELSE 0
    END AS days_since_creation,
    
    CASE
        WHEN i.due_date IS NOT NULL AND i.due_date < CURRENT_DATE AND i.resolution_date IS NULL
        THEN EXTRACT(EPOCH FROM (CURRENT_DATE - i.due_date))/86400
        ELSE NULL
    END AS days_overdue,
    
    -- Status Flags
    CASE
        WHEN i.due_date IS NOT NULL AND 
             ((i.resolution_date IS NOT NULL AND i.resolution_date > i.due_date) OR
              (i.resolution_date IS NULL AND CURRENT_DATE > i.due_date))
        THEN TRUE
        ELSE FALSE
    END AS is_overdue,
    
    CASE
        WHEN i.status_category = 'Done' THEN TRUE
        ELSE FALSE
    END AS is_completed,
    
    CASE
        WHEN i.created_date >= CURRENT_DATE - INTERVAL '7 days' THEN TRUE
        ELSE FALSE
    END AS is_recent,
    
    -- Activity Metrics
    COALESCE(ic.change_count, 0) AS change_count,
    COALESCE(ic.status_change_count, 0) AS status_change_count,
    COALESCE(ic.assignee_change_count, 0) AS assignee_change_count,
    
    -- Additional Categorization
    CASE
        WHEN i.status_category = 'To Do' THEN 'Backlog'
        WHEN i.status_category = 'In Progress' THEN 'In Progress'
        WHEN i.status_category = 'Done' THEN 'Completed'
        ELSE 'Other'
    END AS work_status,
    
    CASE
        WHEN i.created_date >= CURRENT_DATE - INTERVAL '7 days' THEN 'This Week'
        WHEN i.created_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'This Month'
        WHEN i.created_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'Last 3 Months'
        ELSE 'Older'
    END AS age_bucket,
    
    -- Snapshot Metadata
    CURRENT_TIMESTAMP AS snapshot_dttm,
    CURRENT_DATE AS snapshot_date,
    'CUMULATIVE_SNAPSHOT' AS fact_type

FROM 
    {{ ref('stg_jira_issues') }} i
LEFT JOIN
    issue_changelog ic ON i._dlt_id = ic.issue_dlt_id
LEFT JOIN
    {{ ref('stg_jira_users') }} u ON i.assignee_id = u.account_id
LEFT JOIN
    {{ ref('stg_jira_users') }} r ON i.reporter_id = r.account_id
LEFT JOIN
    {{ ref('stg_jira_projects') }} p ON i.project_id = p.project_id