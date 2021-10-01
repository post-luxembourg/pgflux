SELECT
    datname,
    COALESCE(MAX(extract(EPOCH FROM NOW() - query_start)), 0),
    COALESCE(MAX(extract(EPOCH FROM NOW() - xact_start)), 0)
FROM pg_stat_activity
WHERE current_query NOT LIKE '<IDLE%'
GROUP BY datname;
