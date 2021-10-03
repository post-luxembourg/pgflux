SELECT
    datname AS "tag:database",
    pg_database_size(datname) AS "size",
    EXTRACT(EPOCH FROM NOW()) * 1E9 AS "timestamp"
FROM pg_database WHERE datistemplate=false
