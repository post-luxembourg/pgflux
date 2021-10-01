SELECT
    datname,
    COALESCE(MAX(extract(EPOCH FROM NOW() - query_start)), 0),
    COALESCE(MAX(extract(EPOCH FROM NOW() - xact_start)), 0)
FROM pg_stat_activity
WHERE state NOT LIKE '%idle%'
GROUP BY datname;
