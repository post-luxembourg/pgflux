SELECT
    datname AS "tag:database",
    pg_stat_get_db_xact_commit(oid),
    pg_stat_get_db_xact_rollback(oid)
FROM pg_database;
