SELECT
    datname AS "tag:database",
    temp_bytes
FROM
    pg_stat_database;
