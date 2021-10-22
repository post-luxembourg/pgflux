Usage
=====

.. note::

    See also: :ref:`configuration`

Quickstart
----------

With only the ``PGFLUX_POSTGRES_DSN`` value set you can run::

    pgflux --all

This runs all available queries against the given database cluster and writes
the result to ``stdout``.


Help
----

For quick help, you can run::

    pgflux --help

Outputs
-------

``pgflux`` supports different outputs. By default it bundles with ``stdout``,
``http`` and ``https``. To see the available outputs, run::

    pgflux --list-outputs

This will also include any environment variables needed by that output.

The bundled outputs are:

``stdout``
    Write data to standard output

``http`` / ``https``
    Write the data directly into InfluxDB using HTTP(s) POST requests. This
    requires additional environment variables (see the output of
    ``--list-outputs``).


Queries
-------

See :ref:`queries`
