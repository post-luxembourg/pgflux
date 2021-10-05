SELECT
    datname AS "tag:database",
    temp_bytes,
    EXTRACT(EPOCH FROM NOW()) * 1E9 AS "timestamp"
FROM
    pg_stat_database;
