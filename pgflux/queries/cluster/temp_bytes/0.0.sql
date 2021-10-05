SELECT
    datname AS "tag:database",
    temp_bytes,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM
    pg_stat_database;
