"""
This file contains example unit-tests using pytest and classical unit-tests.
"""
from pathlib import Path
from unittest.mock import Mock

import pytest

import pgflux.core as core


@pytest.mark.parametrize(
    "version_num, expected",
    [
        (100_000, core.PgVersion(10, 0)),
        (100_001, core.PgVersion(10, 1)),
        (110_000, core.PgVersion(11, 0)),
        (90_105, core.PgVersion(9, 1)),
        (90_200, core.PgVersion(9, 2)),
    ],
)
def test_get_version(version_num: int, expected: core.PgVersion):
    """
    Ensure we properly parse the numerical server version
    """
    mocked_cursor = Mock()
    mocked_cursor.fetchone.return_value = (version_num,)  # type: ignore

    result = core.get_pg_version(mocked_cursor)
    assert result == expected


@pytest.mark.parametrize(
    "server_version, name, expected",
    [
        (core.PgVersion(9, 2), "connections", "old-query"),
        (core.PgVersion(10, 0), "connections", "connections-10.0"),
        (core.PgVersion(12, 0), "connections", "connections-10.0"),
        (core.PgVersion(9, 2), "unknown-query", ""),
        (core.PgVersion(12, 0), "unknown-query", ""),
    ],
)
def test_get_query(server_version: core.PgVersion, name: str, expected: str):
    """
    We want to load the query dynamically for the proper Postgres version
    """
    queries = {
        "connections": {
            core.PgVersion(0, 0): "old-query",
            core.PgVersion(10, 0): "connections-10.0",
        }
    }
    result = core.get_query(queries, name, server_version)
    assert result == expected


def test_load_queries():
    """
    Ensure that we can properly load the bundled queries
    """
    queries = core.load_queries()
    assert queries.cluster["connections"][core.PgVersion(0, 0)] != ""
    assert queries.cluster["connections"][core.PgVersion(9, 2)] != ""
    assert queries.cluster["connections"][core.PgVersion(10, 0)] != ""
    assert queries.db["index_io"][core.PgVersion(0, 0)] != ""


def test_execute_global_query():
    """
    Ensure we can run "global" queries against the whole cluster conveniently
    """
    queries = core.load_queries()
    with core.connect() as connection:
        result = list(
            core.execute_global(connection, queries.cluster, "connections")
        )
    for row in result:
        assert isinstance(row, dict)


def test_execute_local_query():
    """
    Ensure we can run "local" queries against a single db conveniently
    """
    queries = core.load_queries()
    with core.connect() as connection:
        result = list(
            core.execute_local(connection, queries.db, "dbname", "index_io")
        )
    for row in result:
        assert isinstance(row, dict)


def test_check_queries():
    """
    Ensure all bundled queries are executable
    """
    queries = core.load_queries()
    with core.connect() as connection:
        for query in queries.cluster:
            list(core.execute_global(connection, queries.cluster, query))
        for query in queries.db:
            list(core.execute_local(connection, queries.db, "postgres", query))


def test_get_query_filename():
    result = core.get_query_filename(
        core.PgVersion(10, 0), "cluster", "connections"
    )
    expected = str(
        Path(__file__).parent.parent
        / "pgflux/queries/cluster/connections/10.0.sql"
    )
    assert result == expected
