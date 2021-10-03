SELECT
    COALESCE(SUM(idx_scan), 0) AS idx_scan,
    COALESCE(SUM(seq_scan), 0) AS seq_scan,
    EXTRACT(EPOCH FROM NOW()) * 1E9 AS "timestamp"
FROM pg_stat_user_tables;
