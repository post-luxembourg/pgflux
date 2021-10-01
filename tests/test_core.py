"""
This file contains example unit-tests using pytest and classical unit-tests.
"""
from unittest.mock import Mock

import pytest

import pgflux.core as core


@pytest.fixture
def example_fixture():
    # Do any setup code before the "yield"
    sample_fixture_data = {"hello": "world"}
    try:
        yield sample_fixture_data
    finally:
        pass
        # Do cleanup in the "finally" block


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
    result = core.load_queries()
    assert result["connections"][core.PgVersion(0, 0)] != ""
    assert result["connections"][core.PgVersion(9, 2)] != ""
    assert result["connections"][core.PgVersion(10, 0)] != ""
