pgflux
======

A simple Python utility to send PostgreSQL metrics to InfluxDB


Development
===========

* Set up development environment::

    fab develop

* Run a docker container for testing::

    docker run --rm \
        -e POSTGRES_PASSWORD=mys3cr37passw0rd \
        -p <hostport>:5432 \
        postgresql:latest

* Create a ``.env`` file (use ``.env.template`` as guide)::

    PGFLUX_DSN=postgresql://postgres:mys3cr37passw0rd@localhost:<hostport>/postgres

* Run the tests::

    ./env/bin/pytest
