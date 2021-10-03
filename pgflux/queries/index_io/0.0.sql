SELECT
    COALESCE(SUM(idx_blks_read), 0) AS idx_blks_read,
    COALESCE(SUM(idx_blks_hit), 0) AS idx_blks_hit,
    EXTRACT(EPOCH FROM NOW()) * 1E9 AS "timestamp"
FROM pg_statio_user_indexes;
