SELECT
    COALESCE(SUM(blks_read), 0) AS blks_read,
    COALESCE(SUM(blks_hit), 0) AS blks_hit,
    EXTRACT(EPOCH FROM NOW()) * 1E9 AS "timestamp"
FROM pg_statio_user_sequences;
