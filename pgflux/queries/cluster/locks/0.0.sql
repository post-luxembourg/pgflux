SELECT
    db.datname as "tag:database",
    LOWER(mode) AS "tag:mode",
    locktype AS "tag:locktype",
    granted AS "tag:granted",
    COUNT(mode),
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM pg_database db
INNER JOIN pg_locks lck ON (db.oid=lck.database)
GROUP BY db.datname, mode, locktype, granted
;
