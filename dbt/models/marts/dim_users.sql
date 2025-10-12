{{
    config(
        materialized='table',
        unique_key='user_key',
        on_schema_change='append_new_columns'
    )
}}

WITH user_activity AS (
    SELECT
        assignee_id AS account_id,
        COUNT(DISTINCT issue_id) AS assigned_issues,
        MIN(created_date) AS first_assignment_date,
        MAX(updated_date) AS last_activity_date,
        COUNT(DISTINCT CASE WHEN status_category = 'Done' THEN issue_id END) AS completed_issues,
        COUNT(DISTINCT project_id) AS projects_count
    FROM
        {{ ref('stg_jira_issues') }}
    WHERE
        assignee_id IS NOT NULL
    GROUP BY
        assignee_id
),

reporter_activity AS (
    SELECT
        reporter_id AS account_id,
        COUNT(DISTINCT issue_id) AS reported_issues,
        MIN(created_date) AS first_reported_date,
        MAX(created_date) AS last_reported_date
    FROM
        {{ ref('stg_jira_issues') }}
    WHERE
        reporter_id IS NOT NULL
    GROUP BY
        reporter_id
),

user_snapshot AS (
    SELECT 
        u.account_id,
        u.display_name,
        u.email_address,
        u.active,
        u.time_zone,
        COALESCE(ua.assigned_issues, 0) AS assigned_issues,
        COALESCE(ra.reported_issues, 0) AS reported_issues,
        COALESCE(ua.completed_issues, 0) AS completed_issues,
        CASE 
            WHEN COALESCE(ua.assigned_issues, 0) = 0 THEN 0::numeric
            ELSE (COALESCE(ua.completed_issues, 0)::numeric / COALESCE(ua.assigned_issues, 1)::numeric * 100)
        END AS completion_rate,
        ua.first_assignment_date,
        ua.last_activity_date,
        ra.first_reported_date,
        ra.last_reported_date,
        COALESCE(ua.projects_count, 0) AS projects_count,
        CASE
            WHEN u.active = FALSE THEN 'Inactive'
            WHEN COALESCE(ua.assigned_issues, 0) = 0 AND COALESCE(ra.reported_issues, 0) = 0 THEN 'No Activity'
            WHEN ua.last_activity_date >= CURRENT_DATE - INTERVAL '7 days' THEN 'Recent Activity'
            WHEN ua.last_activity_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
            ELSE 'Inactive'
        END AS activity_status,
        CURRENT_TIMESTAMP AS valid_from_dttm,
        CURRENT_TIMESTAMP AS updated_dttm
    FROM 
        {{ ref('stg_jira_users') }} u
    LEFT JOIN
        user_activity ua ON u.account_id = ua.account_id
    LEFT JOIN
        reporter_activity ra ON u.account_id = ra.account_id
)

SELECT 
    -- SCD Keys
    account_id AS user_key,
    account_id AS user_id,
    
    -- Business Keys
    account_id,
    display_name,
    email_address,
    
    -- Attributes
    active,
    time_zone,
    assigned_issues,
    reported_issues,
    completed_issues,
    completion_rate,
    first_assignment_date,
    last_activity_date,
    first_reported_date,
    last_reported_date,
    projects_count,
    activity_status,
    
    -- SCD Type 1 Fields
    TRUE AS is_current,
    valid_from_dttm,
    NULL::timestamp AS valid_to_dttm,
    updated_dttm,
    
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'SCD_TYPE_1' AS scd_type

FROM user_snapshot