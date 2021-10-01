SELECT datname, pg_database_size(datname)
FROM pg_database WHERE datistemplate=false
