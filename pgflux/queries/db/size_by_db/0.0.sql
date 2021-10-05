-- TODO: This only works for the current connection I think? Do we need to open
-- a separate connection for each DB? I hope not!
SELECT
    SUM(pg_relation_size(oid, 'main')) AS main_size,
    SUM(pg_relation_size(oid, 'vm')) AS vm_size,
    SUM(pg_relation_size(oid, 'fsm')) AS fsm_size,
    SUM(
        CASE reltoastrelid
        WHEN 0 THEN 0
        ELSE pg_total_relation_size(reltoastrelid)
        END
    ) AS toast_size,
    SUM(pg_indexes_size(oid)) AS indexes_size,
    pg_database_size(current_database()) AS database_size,
    EXTRACT(EPOCH FROM NOW()) * 1E9 AS "timestamp"
    FROM pg_class
    WHERE relkind not in ('t', 'i')
    AND NOT relisshared;
