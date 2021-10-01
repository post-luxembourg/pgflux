SELECT
    SUM(idx_scan) AS idx_scan,
    SUM(seq_scan) AS seq_scan
FROM pg_stat_user_tables;
