.. _queries:

Queries
=======

``pgflux`` comes with several bundled queries. They can be listed with::

    pgflux --list-queries

To run all queries, use ``--all``::

    pgflux --all

To run only *some* queries, use them as positional arguments::

    pgflux db:disk_id cluster:locks


Extending with new Queries & Execution Details
----------------------------------------------

See :ref:`query-mainenance`


Query Scopes
------------

Queries are separated into two groups:

**Cluster Global** (prefix: ``cluster``)
    These queries can be run on any connection. In ``pgflux`` they will
    use the connection defined by the ``PGFLUX_POSTGRES_DSN``
    environment variable.

**Database Local** (prefix: ``db``)
    These queries return statistics from the *currently connected*
    database.

    When fetching metrics, ``pgflux`` will reuse the credentials from the
    ``PGFLUX_POSTGRES_DSN`` environment variable and open a new
    connection on each of those databases to fetch the metrics.
