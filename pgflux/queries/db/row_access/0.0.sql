SELECT
    COALESCE(SUM(n_tup_ins), 0) AS n_tup_ins,
    COALESCE(SUM(n_tup_upd), 0) AS n_tup_upd,
    COALESCE(SUM(n_tup_del), 0) AS n_tup_del,
    COALESCE(SUM(n_tup_hot_upd), 0) AS n_tup_hot_upd,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM pg_stat_user_tables;
