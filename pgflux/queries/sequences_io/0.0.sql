SELECT
    SUM(blks_read) AS blks_read,
    SUM(blks_hit) AS blks_hit
FROM pg_statio_user_sequences;
