.. _development:

Development & Maintenance
=========================

Development Environment
-----------------------

We use fabric_ as development helper. All tasks are defined in ``fabfile.py`` in
the root source tree. If you don't want to use ``fabric``, that file should
contain enough information to get started.

To set up a basic development environment simply run::

    fab develop

The project can read environment variables from a ``.env`` file. A template can
be found in ``.env.template``. By running ``fab develop`` a basic env-file will
be materialised.

A collection of docker-containers with PostgreSQL, InfluxDB and Grafana are
provided via a ``docker-compose`` file and can be run using::

    fab run-dev-containers

Once the containers are running, ``pgflux`` should be able to connect and run.
The following command should show output::

    ./env/bin/pgflux --all

If that works, it will be possible to start collecting metrics using something
like the following::

    watch -n 300 ./env/bin/pgflux --all -o http

The environment-variables in ``.env`` should be set up to send HTTP traffic to
the container from the docker-compose file.

Note that the sample dashboard has a minimum granularity of 5 minutes, so
sending more often than that does not make a lot of sense.

Once the first data point is collected (immediatly after ``pgflux`` was executed
with the ``http`` output) we can inspect the data in Grafana.

Connect to http://localhost:3000 (provided via the docker-compose file) and log
in using ``admin``/``admin``. It should ask you to reset the password.

Grafana Setup
-------------

InfluxDB Data Source
~~~~~~~~~~~~~~~~~~~~

The "InfluxDB" host inside the docker-compose stack is called ``influx``. With
that in mind:

* In Grafana, navigate to "Configuration" (the Cog icon) -> Data sources
* Click on "Add data source"
* Select InfluxDB
* Use the following settings:

  Name
    InfluxDB *(this value is referenced in the dashboard template. If you change
    it here, it must also be changed in the dashboard JSON file)*
  URL
    http://influx:8086
  Database
    postgres_stats

* Click on "Save & Test". The data source should now be working. If it does not,
  make sure you followed the instructions from before properly.


Testing the Data Source
~~~~~~~~~~~~~~~~~~~~~~~

* In Grafana, navigate to "Explore" (the compass icon)
* Ensure that "InfluxDB" (our data-source) is selected in the top-left
  drop-down.
* Click on "select measurement".

If you see items in that drop-down box, the setup is working and we can continue
on to a dashboard.


.. _sample-dashboard:

Sample Dashboard
~~~~~~~~~~~~~~~~

* Open the file `grafana-dashboard.json.template`_ from the project source tree.
* In Grafana, navigate to "Create" (the "+" icon) -> "Import"
* Click on "Upload JSON File"
* Select the template file (as linked above)
* Click on "Import"

You should now see the dashboard. If no values appear yet, give it at lease 5
minutes because the minimum "interval" is set to 5 minutes in almost every
graph.

.. _grafana-dashboard.json.template: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post4/grafana-dashboard.json.template
.. _fabric: https://fabfile.org


.. _query-mainenance:

Query Development & Maintenance
-------------------------------

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

    * ... ``global_sizes`` as measurement name (taken from the filename/path)
    * ... a tag with the name "database" and the values using the
      "datname" column of ``pg_database``
    * ... a field with the name ``size`` and the value taken from
      ``pg_database_size()``.
    * ... the current time as InfluxDB timestamp.
