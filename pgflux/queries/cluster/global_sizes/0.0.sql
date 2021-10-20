SELECT
    datname AS "tag:database",
    pg_database_size(datname) AS size,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM pg_database WHERE datistemplate=false
