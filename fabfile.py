# pylint: skip-file
"""
Application development tasks
"""

from fabric import Connection
from fabrips.tasks import inject
from invoke import Context, task

inject(globals())


@task
def develop(context, unattended=False):
    """
    Set up a development environment
    """
    from fabrips.core import develop as develop_

    # perform any steps before package installation here

    develop_(context)

    # create any required config-files here. See fabrips.core.create_config for
    # a useful helper method
