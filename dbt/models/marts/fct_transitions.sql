{{
    config(
        materialized='table',
        unique_key='transition_key',
        on_schema_change='append_new_columns'
    )
}}

WITH issue_transitions AS (
    SELECT
        cl.history_id,
        cl.issue_dlt_id,
        cl.author_id,
        cl.change_date,
        cl.field,
        cl.from_string,
        cl.to_string,
        i.issue_key,
        i.issue_id,
        i.project_id,
        i.assignee_id,
        i.reporter_id,
        i.issue_type,
        i.priority,
        i.created_date,
        i.resolution_date,
        -- Create a unique key for each transition
        CONCAT(cl.issue_dlt_id, '_', cl.history_id, '_', cl.field) AS transition_key
    FROM
        {{ ref('stg_jira_changelog') }} cl
    INNER JOIN
        {{ ref('stg_jira_issues') }} i ON cl.issue_dlt_id = i._dlt_id
    WHERE
        cl.field IN ('status', 'assignee', 'priority', 'issuetype')
),

status_transitions AS (
    SELECT
        *,
        CASE
            WHEN field = 'status' THEN
                CASE
                    WHEN to_string IN ('To Do', 'Open', 'Backlog') THEN 'Backlog'
                    WHEN to_string IN ('In Progress', 'In Development', 'Active') THEN 'In Progress'
                    WHEN to_string IN ('Review', 'In Review', 'Testing', 'Code Review') THEN 'Review'
                    WHEN to_string IN ('Done', 'Closed', 'Resolved', 'Completed') THEN 'Done'
                    ELSE 'Other'
                END
            ELSE NULL
        END AS status_category,
        
        CASE
            WHEN field = 'status' THEN
                CASE
                    WHEN to_string IN ('To Do', 'Open', 'Backlog') THEN 1
                    WHEN to_string IN ('In Progress', 'In Development', 'Active') THEN 2
                    WHEN to_string IN ('Review', 'In Review', 'Testing', 'Code Review') THEN 3
                    WHEN to_string IN ('Done', 'Closed', 'Resolved', 'Completed') THEN 4
                    ELSE 0
                END
            ELSE NULL
        END AS status_order
    FROM
        issue_transitions
),

transition_metrics AS (
    SELECT
        *,
        -- Calculate time in previous status
        LAG(change_date) OVER (
            PARTITION BY issue_dlt_id, field 
            ORDER BY change_date
        ) AS previous_change_date,
        
        -- Calculate time since creation
        EXTRACT(EPOCH FROM (change_date - created_date))/86400 AS days_since_creation,
        
        -- Calculate time to resolution (if resolved)
        CASE
            WHEN resolution_date IS NOT NULL AND field = 'status' AND to_string IN ('Done', 'Closed', 'Resolved')
            THEN EXTRACT(EPOCH FROM (resolution_date - created_date))/86400
            ELSE NULL
        END AS days_to_resolution
    FROM
        status_transitions
)

SELECT 
    -- Primary Keys
    transition_key,
    history_id,
    issue_dlt_id,
    
    -- Business Keys
    issue_key,
    issue_id,
    project_id,
    assignee_id,
    reporter_id,
    
    -- Transition Details
    field AS transition_field,
    from_string AS from_value,
    to_string AS to_value,
    change_date AS transition_date,
    author_id AS transition_author_id,
    
    -- Issue Context
    issue_type,
    priority,
    created_date AS issue_created_date,
    resolution_date AS issue_resolution_date,
    
    -- Status Categorization
    status_category,
    status_order,
    
    -- Time Metrics
    previous_change_date,
    days_since_creation,
    days_to_resolution,
    
    CASE
        WHEN previous_change_date IS NOT NULL
        THEN EXTRACT(EPOCH FROM (change_date - previous_change_date))/86400
        ELSE NULL
    END AS time_in_previous_status,
    
    -- Transition Type
    CASE
        WHEN field = 'status' THEN 'Status Change'
        WHEN field = 'assignee' THEN 'Assignment Change'
        WHEN field = 'priority' THEN 'Priority Change'
        WHEN field = 'issuetype' THEN 'Type Change'
        ELSE 'Other Change'
    END AS transition_type,
    
    -- Workflow Stage
    CASE
        WHEN field = 'status' AND to_string IN ('To Do', 'Open', 'Backlog') THEN 'Backlog'
        WHEN field = 'status' AND to_string IN ('In Progress', 'In Development', 'Active') THEN 'Development'
        WHEN field = 'status' AND to_string IN ('Review', 'In Review', 'Testing', 'Code Review') THEN 'Review'
        WHEN field = 'status' AND to_string IN ('Done', 'Closed', 'Resolved', 'Completed') THEN 'Completed'
        ELSE 'Other'
    END AS workflow_stage,
    
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'TRANSACTION_FACT' AS fact_type

FROM
    transition_metrics
