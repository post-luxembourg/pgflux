SELECT
    SUM(heap_blks_read) AS heap_blks_read,
    SUM(heap_blks_hit) AS heap_blks_hit,
    SUM(idx_blks_read) AS idx_blks_read,
    SUM(idx_blks_hit) AS idx_blks_hit,
    SUM(toast_blks_read) AS toast_blks_read,
    SUM(toast_blks_hit) AS toast_blks_hit,
    SUM(tidx_blks_read) AS tidx_blks_read
FROM pg_statio_user_tables;
