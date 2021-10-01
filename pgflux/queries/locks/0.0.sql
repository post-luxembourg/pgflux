SELECT
    db.datname,
    LOWER(mode),
    locktype,
    granted,
    COUNT(mode)
FROM pg_database db
FULL OUTER JOIN pg_locks lck ON (db.oid=lck.database)
GROUP BY db.datname, mode, locktype, granted;
