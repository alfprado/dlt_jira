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
    {% if var('load_users', true) %}
        {{ source('jira_data', 'users') }}
    {% else %}
        (SELECT NULL::text AS account_id, NULL::text AS display_name, NULL::text AS email_address, NULL::boolean AS active, NULL::text AS time_zone, NULL::text AS _dlt_id WHERE 1=0) AS users
    {% endif %}
