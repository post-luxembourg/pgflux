SELECT
    datname AS "tag:database",
    COALESCE(MAX(extract(EPOCH FROM NOW() - query_start)), 0) AS "query_start",
    COALESCE(MAX(extract(EPOCH FROM NOW() - xact_start)), 0) AS "xact_start",
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM pg_stat_activity
WHERE state NOT LIKE '%idle%'
GROUP BY datname;
