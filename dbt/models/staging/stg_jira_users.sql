{{
    config(
        materialized='view'
    )
}}

SELECT 
    -- Primary key
    account_id,
    
    -- User information
    display_name,
    email_address,
    
    -- User status
    active,
    
    -- User preferences
    time_zone,
    
    -- Additional metadata
    _dlt_id

FROM 
    {{ source('jira_data', 'users') }}
