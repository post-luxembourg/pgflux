pgflux
======

A simple Python utility to send PostgreSQL metrics to InfluxDB


Development
===========

NOTE
----

This project uses ``fabric`` as task runner (see https://fabfile.org). To
install it use either ``pipx install fabric`` (recommended) or, if you don't
have ``pipx``: ``pip install --user fabric``.

Commands
--------

* To set up or refresh the development environment::

    fab develop

* Environment Variables can be set via a ``.env`` file (see ``.env.template``
  as example).

* Run a PostgreSQL instance for testing::

  fab run-postgres-container

* Run a InfluxDB instance for testing::

  fab run-influx-container

* Run the tests::

    ./env/bin/pytest
