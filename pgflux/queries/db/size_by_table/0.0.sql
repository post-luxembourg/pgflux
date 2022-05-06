SELECT
    nsp.nspname || '.' || relname AS "tag:table",
    relnamespace,
    reltuples as num_tuples,
    pg_relation_size(pg_class.oid, 'main') AS main_size,
    pg_relation_size(pg_class.oid, 'vm') AS vm_size,
    pg_relation_size(pg_class.oid, 'fsm') AS fsm_size,
    CASE reltoastrelid
        WHEN 0 THEN 0
        ELSE pg_total_relation_size(reltoastrelid)
        END
    AS toast_size,
    pg_indexes_size(pg_class.oid) AS indexes_size,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
    FROM pg_class
    INNER JOIN pg_namespace AS nsp ON (nsp.oid=pg_class.relnamespace)
    WHERE relkind = 'r'
    AND relnamespace NOT IN (SELECT oid FROM pg_namespace WHERE nspname IN ('information_schema', 'pg_catalog'))
    AND NOT relisshared
    ;
