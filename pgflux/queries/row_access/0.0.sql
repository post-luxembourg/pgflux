SELECT
    SUM(n_tup_ins) AS n_tup_ins,
    SUM(n_tup_upd) AS n_tup_upd,
    SUM(n_tup_del) AS n_tup_del,
    SUM(n_tup_hot_upd) AS n_tup_hot_upd
FROM pg_stat_user_tables;
