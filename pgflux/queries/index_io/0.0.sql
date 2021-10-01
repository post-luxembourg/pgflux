SELECT
    SUM(idx_blks_read) AS idx_blks_read,
    SUM(idx_blks_hit) AS idx_blks_hit
FROM pg_statio_user_indexes;
