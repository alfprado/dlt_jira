{{
    config(
        materialized='view'
    )
}}

WITH changelog_histories AS (
    SELECT 
        id AS history_id,
        _dlt_parent_id AS issue_dlt_id,
        author__account_id AS author_id,
        created::timestamp AS change_date,
        _dlt_id
    FROM 
        {{ source('jira_data', 'issues__changelog__histories') }}
),

changelog_items AS (
    SELECT 
        _dlt_parent_id AS history_dlt_id,
        field,
        from_string,
        to_string,
        _dlt_id
    FROM 
        {{ source('jira_data', 'issues__changelog__histories__items') }}
)

SELECT 
    -- Primary keys
    ch.history_id,
    ch.issue_dlt_id,
    
    -- Change information
    ch.author_id,
    ch.change_date,
    ci.field,
    ci.from_string,
    ci.to_string,
    
    -- Additional metadata
    ch._dlt_id AS history_dlt_id,
    ci._dlt_id AS item_dlt_id

FROM 
    changelog_histories ch
LEFT JOIN 
    changelog_items ci ON ch._dlt_id = ci.history_dlt_id
