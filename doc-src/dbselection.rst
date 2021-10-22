Database Selection
==================

By default ``pgflux`` runs against every database on the cluster. To exclude
some databases, use the ``--exclude`` argument::

    pgflux --exclude ".*bak.*"

The value for ``--exclude`` is a regular expression. Any database-name that
matches the regex will be skipped.
