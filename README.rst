pgflux
======

``pgflux`` is a Python utility to send PostgreSQL metrics to InfluxDB. The
drivers when developing this tool were:

* **Make it easy to extend:** Authoring new queries should *only* require
  PostgreSQL knowledge to allow non-devs to easily add/fix/modify the collected
  metrics. ``pgflux`` does not require you to know Python, InfluxDB nor Grafana
  to work on the provided SQL queries.
* **Be independently runnable:** ``pgflux`` should be runnable without first
  setting up a hugely complex dev-environment. All that is needed is a Python
  environment and a PostgreSQL server (a Dockerfile for testing is supplied for
  the latter).

Screenshots
-----------

It enables Grafana visualisations as seen in the screenshots below:

.. image:: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.1/docs/_images/grafana-dashboard-01.png
  :target: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.1/docs/_images/grafana-dashboard-01.png

.. image:: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.1/docs/_images/grafana-dashboard-02.png
  :target: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.1/docs/_images/grafana-dashboard-02.png

.. image:: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.1/docs/_images/grafana-dashboard-03.png
  :target: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.1/docs/_images/grafana-dashboard-03.png


Installation
============

The project can be installed directly via ``pip``::

    python3 -m venv /path/to/virtual-env
    /path/to/virtual-env/bin/pip install pgflux

The use of a virtual environment is optional, but recommended.


Usage
=====

See https://post-luxembourg.github.io/pgflux/usage.html


Development & Extending
=======================

For detailed instructions, see https://post-luxembourg.github.io/pgflux/development.html


NOTE
----

This project uses ``fabric`` as task runner (see https://fabfile.org). To
install it use either ``pipx install fabric`` (recommended) or, if you don't
have ``pipx``: ``pip install --user fabric``.

Commands
--------

* Listing all available development tasks::

    fab -l

* To set up or refresh the development environment::

    fab develop

* Run PostgreSQL, InfluxDB & Grafana containers (requires ``docker-compose``)::

    fab run-dev-containers

* Run the tests::

    fab test
