{{
    config(
        materialized='table',
        unique_key=['user_id', 'project_id', 'status_category', 'time_period'],
        on_schema_change='append_new_columns'
    )
}}

WITH user_issues AS (
    SELECT 
        assignee_id AS user_id,
        project_id,
        project_key,
        project_name,
        status,
        status_category,
        issue_type,
        priority,
        issue_id,
        issue_key,
        created_date,
        updated_date,
        resolution_date,
        due_date,
        CASE 
            WHEN resolution_date IS NOT NULL 
            THEN EXTRACT(EPOCH FROM (resolution_date - created_date))/86400 
            ELSE NULL 
        END AS days_to_resolution,
        CASE
            WHEN due_date IS NOT NULL AND 
                ((resolution_date IS NOT NULL AND resolution_date > due_date) OR
                 (resolution_date IS NULL AND CURRENT_DATE > due_date))
            THEN TRUE
            ELSE FALSE
        END AS is_overdue,
        CASE
            WHEN DATE_TRUNC('month', created_date) = DATE_TRUNC('month', CURRENT_DATE) THEN 'Current Month'
            WHEN DATE_TRUNC('month', created_date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') THEN 'Last Month'
            WHEN created_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'Last 3 Months'
            ELSE 'Older'
        END AS time_period
    FROM 
        {{ ref('stg_jira_issues') }}
    WHERE 
        assignee_id IS NOT NULL
),

user_reported_issues AS (
    SELECT 
        reporter_id AS user_id,
        COUNT(DISTINCT issue_id) AS reported_issues,
        COUNT(DISTINCT CASE WHEN status_category = 'Done' THEN issue_id END) AS resolved_reported_issues
    FROM 
        {{ ref('stg_jira_issues') }}
    WHERE 
        reporter_id IS NOT NULL
    GROUP BY 
        reporter_id
),

user_activity AS (
    SELECT
        issue_dlt_id,
        field,
        from_string,
        to_string,
        change_date,
        author_id AS user_id
    FROM
        {{ ref('stg_jira_changelog') }}
    WHERE
        author_id IS NOT NULL
)

SELECT 
    ui.user_id,
    u.display_name AS user_name,
    u.email_address AS user_email,
    u.active AS is_active,
    ui.project_id,
    ui.project_key,
    ui.project_name,
    ui.status_category,
    ui.time_period,
    
    -- Issue counts
    COUNT(DISTINCT ui.issue_id) AS assigned_issues,
    COUNT(DISTINCT CASE WHEN ui.status_category = 'Done' THEN ui.issue_id END) AS completed_issues,
    COUNT(DISTINCT CASE WHEN ui.is_overdue THEN ui.issue_id END) AS overdue_issues,
    COUNT(DISTINCT CASE WHEN ui.issue_type = 'Bug' THEN ui.issue_id END) AS bug_count,
    COUNT(DISTINCT CASE WHEN ui.priority = 'High' OR ui.priority = 'Highest' THEN ui.issue_id END) AS high_priority_issues,
    
    -- Time metrics
    MIN(ui.created_date) AS earliest_issue_date,
    MAX(ui.updated_date) AS latest_update_date,
    AVG(ui.days_to_resolution) AS avg_days_to_resolution,
    MIN(ui.days_to_resolution) AS min_days_to_resolution,
    MAX(ui.days_to_resolution) AS max_days_to_resolution,
    
    -- Completion rate
    CASE 
        WHEN COUNT(DISTINCT ui.issue_id) = 0 THEN 0::numeric
        ELSE (COUNT(DISTINCT CASE WHEN ui.status_category = 'Done' THEN ui.issue_id END)::numeric / 
              COUNT(DISTINCT ui.issue_id)::numeric * 100)
    END AS completion_rate,
    
    -- On-time delivery rate
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN ui.due_date IS NOT NULL THEN ui.issue_id END) = 0 THEN NULL
        ELSE (COUNT(DISTINCT CASE WHEN ui.due_date IS NOT NULL AND NOT ui.is_overdue THEN ui.issue_id END)::numeric / 
              COUNT(DISTINCT CASE WHEN ui.due_date IS NOT NULL THEN ui.issue_id END)::numeric * 100)
    END AS on_time_delivery_rate,
    
    -- Reported issues
    COALESCE(uri.reported_issues, 0) AS reported_issues,
    COALESCE(uri.resolved_reported_issues, 0) AS resolved_reported_issues,
    
    -- Activity metrics
    COUNT(DISTINCT ua.field) AS activity_fields_changed,
    COUNT(DISTINCT CASE WHEN ua.field = 'status' THEN ua.issue_dlt_id END) AS status_changes,
    
    -- Performance indicators
    CASE
        WHEN COUNT(DISTINCT ui.issue_id) = 0 THEN 'No Issues'
        WHEN (COUNT(DISTINCT CASE WHEN ui.status_category = 'Done' THEN ui.issue_id END)::numeric / 
              NULLIF(COUNT(DISTINCT ui.issue_id)::numeric, 0) * 100) >= 80 THEN 'High Performer'
        WHEN (COUNT(DISTINCT CASE WHEN ui.status_category = 'Done' THEN ui.issue_id END)::numeric / 
              NULLIF(COUNT(DISTINCT ui.issue_id)::numeric, 0) * 100) >= 50 THEN 'Medium Performer'
        ELSE 'Needs Improvement'
    END AS performance_category,
    
    -- Time tracking
    CURRENT_TIMESTAMP AS report_generated_at,
    CURRENT_DATE AS report_date

FROM 
    user_issues ui
LEFT JOIN 
    {{ ref('stg_jira_users') }} u ON ui.user_id = u.account_id
LEFT JOIN
    user_reported_issues uri ON ui.user_id = uri.user_id
LEFT JOIN
    user_activity ua ON ui.user_id = ua.user_id
GROUP BY 
    ui.user_id, u.display_name, u.email_address, u.active,
    ui.project_id, ui.project_key, ui.project_name, 
    ui.status_category, ui.time_period,
    uri.reported_issues, uri.resolved_reported_issues