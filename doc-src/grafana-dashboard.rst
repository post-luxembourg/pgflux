Grafana Dashboard
=================

The project does *not* automatcially create a dashboard in Grafana. It only
sends metrics to InfluxDB.

For convenience, a sample dashboard resides in the source-tree (see
https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post4/grafana-dashboard.json.template).

To use this file **replace all occurrences of** ``{{data-source-name}}`` with
your InfluxDB data-source in Grafana before importing!
