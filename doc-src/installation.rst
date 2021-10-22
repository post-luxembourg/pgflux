Installation
============

The project is published on pypi_ and can be installed via ``pip``::

    pip install pgflux


.. _pypi: https://pypi.python.org/project/pgflux

.. _configuration:

Configuration
-------------

All remote-connection details are configured via environment-variables. The
only "core" environment variable is ``PGFLUX_POSTGRES_DSN``. This is used to
open a connection to the PostgreSQL cluster to fetch the statistics. Example::

    PGFLUX_POSTGRES_DSN=postgresql://postgres:mys3cr37@localhost/postgres

The DSN value is passed directly into :py:func:`psycopg2.connect`. See its
documentation for details on DSN formatting.
