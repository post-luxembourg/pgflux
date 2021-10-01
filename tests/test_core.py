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
