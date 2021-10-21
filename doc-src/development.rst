.. _development:

Development & Maintenance
=========================

Queries
-------

Folder Structure & Version Matching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bundled query files are located in ``pgflux/queries`` of the source tree
with the following structure::

    pgflux/queries
    ├── cluster
    │   ├── connections
    │   │   ├── 0.0.sql
    │   │   ├── 10.0.sql
    │   │   └── 9.2.sql
    ┆   ┆
    │   └── transactions
    │       └── 0.0.sql
    └── db
        └── size_by_db
            └── 0.0.sql


The first level must be either ``cluster`` or ``db``. See :ref:`queries`
for their meaning.

The second level is used as InfluxDB measurement name and must be valid
in that context. The above example contains the measurement names
``connections``, ``transactions`` and ``size_by_db``.

The *filename* must represent the major/minor PostgreSQL version at which
this query was supported. A file with the name ``0.0.sql`` is a wildcard
and is executed against any PostgreSQL version. If multiple files are
found, the query is picked that has the *highest* major/version number
that is still *below* the current PostgreSQL version. For example, with
the queries above, ``connections`` has a definition for ``0.0`` (the
wildcard), ``9.2`` and ``10.0``. The filenames are picked as follows:

* On PostgreSQL 9.0 → Use ``0.0.sql``
* On PostgreSQL 9.2 → Use ``9.2.sql``
* On PostgreSQL 9.4 → Use ``9.2.sql``
* On PostgreSQL 10.5 → Use ``10.0.sql``

This lookup allows us to easily adapt to changes in PostgreSQL.

.. warning::

   It is quite possible that newer PostgreSQL versions provide more
   detailed statistics by adding new columns and/or changing values in
   major releases.

   To keep the InfluxDB manageable it is **strongly** recommended to
   keep the column-names, types and values compatible across the
   versions. See ``pgflux/queries/cluster/connections`` as an example
   where care has been taken to translate some changing values to
   something stable across the different versions.

   However, ``pgflux`` does not *enforce* this.

Query Execution & Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When executing a query, ``pgflux`` does the following:

* Each column prefixed with ``tag:`` will become an InfluxDB tag using
  the column-name as tag-name and column-value as tag-value.

* The column ``timestamp`` is interpreted as **seconds** from "epoch"
  (a classical Unix-Timestamp).

* Every remaining column will be used as InfluxDB measurement values.

* The folder-name containing the query is used as the InfluxDB
  measurement-name.


Example
^^^^^^^

.. code-block:: sql
   :caption: Filename: ``queries/global_sizes/0.0.sql``

    SELECT
        datname AS "tag:database",
        pg_database_size(datname) AS size,
        EXTRACT(EPOCH FROM NOW()) AS "timestamp"
    FROM pg_database WHERE datistemplate=false

This query will create InfluxDB rows with...

    * ... a tag with the name "database" and the values using the
      "datname" column of ``pg_database``
    * ... a field with the name ``size`` and the value taken from
      ``pg_database_size()``.
    * ... the current time as InfluxDB timestamp.
