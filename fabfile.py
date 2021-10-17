# type: ignore
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
def run_dev_containers(context, reset=True):
    """
    Run a set of containers which are useful for development
    """
    try:
        context.run("docker-compose up", pty=True, replace_env=False)
    finally:
        if reset:
            context.run("docker-compose down", pty=True, replace_env=False)


@task
def doc(context):
    context.run("./env/bin/sphinx-apidoc -o doc/api -f pgflux")
    context.run(
        "./env/bin/sphinx-build -a doc/ gh-pages", pty=True, replace_env=False
    )
