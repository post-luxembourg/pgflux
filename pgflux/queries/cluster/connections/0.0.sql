WITH users AS (SELECT usename FROM pg_user),
conntype AS (SELECT u.usename,
    act.pid,
    act.waiting,
    current_query
    FROM users u
    INNER JOIN pg_stat_activity act USING (usename))
SELECT
    usename AS "tag:username",
    COUNT(CASE WHEN current_query='<IDLE>'
        THEN 1 END) AS idle,
    COUNT(CASE WHEN current_query='<IDLE> in transaction'
        THEN 1 END) AS idle_tx,
    COUNT(CASE WHEN current_query='<insufficient privilege>'
        THEN 1 END) AS unknown,
    COUNT(CASE WHEN current_query NOT IN (
        '<IDLE>',
        '<IDLE> in transaction',
        '<insufficient privilege>')
        THEN 1 END) AS query_running,
    COUNT(CASE WHEN waiting THEN 1 END) AS waiting,
    EXTRACT(EPOCH FROM NOW()) AS "timestamp"
FROM conntype
WHERE COALESCE(conntype.pid, 0) <> pg_backend_pid()
GROUP BY usename
ORDER BY usename;
