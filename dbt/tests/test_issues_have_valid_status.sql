-- Test to ensure all issues have a valid status
SELECT
    issue_id,
    issue_key,
    status
FROM {{ ref('fct_issues_details') }}
WHERE status IS NULL OR TRIM(status) = ''
