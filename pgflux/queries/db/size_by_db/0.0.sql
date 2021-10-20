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
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
    FROM pg_class
    WHERE relkind not in ('t', 'i')
    AND NOT relisshared;
