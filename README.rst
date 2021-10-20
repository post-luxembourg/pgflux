pgflux
======

``pgflux`` is a Python utility to send PostgreSQL metrics to InfluxDB. The
drivers when developing this tool were:

It enables Grafana visualisations as seen in the screenshots below:

.. image:: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post1/docs/_images/grafana-dashboard-01.png
  :target: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post1/docs/_images/grafana-dashboard-01.png

.. image:: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post1/docs/_images/grafana-dashboard-02.png
  :target: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post1/docs/_images/grafana-dashboard-02.png

.. image:: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post1/docs/_images/grafana-dashboard-03.png
  :target: https://raw.githubusercontent.com/post-luxembourg/pgflux/v1.0.0.post1/docs/_images/grafana-dashboard-03.png


Installation
============

The project is currently very much usable but not *officially* released yet (no
PyPI packages).

It is however installable via ``git`` or ``http`` directly::

    pip install "git+https://github.com/exhuma/pgflux@initial-release"


Usage
=====

See https://exhuma.github.io/pgflux/usage.html


Development & Extending
=======================

For detailed instructions, see https://exhuma.github.io/pgflux/development.html


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
