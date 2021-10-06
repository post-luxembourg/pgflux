SELECT
    COALESCE(0, SUM(heap_blks_read)) AS heap_blks_read,
    COALESCE(0, SUM(heap_blks_hit)) AS heap_blks_hit,
    COALESCE(0, SUM(idx_blks_read)) AS idx_blks_read,
    COALESCE(0, SUM(idx_blks_hit)) AS idx_blks_hit,
    COALESCE(0, SUM(toast_blks_read)) AS toast_blks_read,
    COALESCE(0, SUM(toast_blks_hit)) AS toast_blks_hit,
    COALESCE(0, SUM(tidx_blks_read)) AS tidx_blks_read,
    COALESCE(0, SUM(tidx_blks_hit)) AS tidx_blks_hit,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM pg_statio_user_tables;
