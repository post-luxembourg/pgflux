# pylint: skip-file
"""
Application development tasks
"""

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
