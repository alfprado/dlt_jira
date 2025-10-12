-- Test to ensure project completion percentage is valid
SELECT
    project_id,
    project_name,
    completion_percentage
FROM {{ ref('dim_projects') }}
WHERE completion_percentage < 0 OR completion_percentage > 100
