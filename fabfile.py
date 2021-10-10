# pylint: skip-file
"""
Application development tasks
"""

from pathlib import Path

from fabric import Connection
from invoke import Context, task


@task
def develop(context):
    """
    Set up a development environment
    """
    context.run("[ -d env ] || python3 -m venv env", replace_env=False)
    context.run("./env/bin/pip install -U pip")
    context.run("./env/bin/pip install -e .[test,dev]")


@task
def run_postgres_container(context):
    """
    Run a simple PostgreSQL container for development/testing
    """
    context.run(
        "docker run --rm "
        "-e POSTGRES_PASSWORD=mys3cr37passw0rd "
        "-p 5432:5432 "
        "postgres:latest",
        pty=True,
        replace_env=False,
    )


@task
def run_influx_container(context):
    """
    Run a simple InfluxDB container for development/testing
    """
    here = str(Path().absolute())
    context.run(
        "docker "
        "run "
        "-p 8086:8086 "
        "--rm "
        "--name influxdb "
        f"--volume {here}/docker-resources/docker-entrypoint-initdb.d:"
        "/docker-entrypoint-initdb.d "
        "influxdb:1.8",
        pty=True,
        replace_env=False,
    )
