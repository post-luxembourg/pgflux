WITH users AS (SELECT usename FROM pg_user),
conntype AS (SELECT u.usename,
    act.pid,
    act.wait_event_type IS NOT NULL as waiting,
    state,
    query
    FROM users u
    INNER JOIN pg_stat_activity act USING (usename))
SELECT
    usename AS "tag:username",
    COUNT(CASE WHEN state = 'idle'
        THEN 1 END) AS idle,
    COUNT(CASE WHEN state like 'idle in transaction%'
        THEN 1 END) AS idle_tx,
    COUNT(CASE WHEN state NOT IN (
        'idle',
        'idle in transaction',
        'idle in transaction (aborted)',
        'active')
        THEN 1 END) AS unknown,
    COUNT(CASE WHEN state = 'active'
        THEN 1 END) AS query_running,
    COUNT(CASE WHEN waiting THEN 1 END) AS waiting,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM conntype
WHERE COALESCE(conntype.pid, 0) <> pg_backend_pid()
GROUP BY usename
ORDER BY usename;
