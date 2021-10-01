"""
This file contains example unit-tests using pytest and classical unit-tests.
"""
import pytest


@pytest.fixture
def example_fixture():
    # Do any setup code before the "yield"
    sample_fixture_data = {"hello": "world"}
    try:
        yield sample_fixture_data
    finally:
        pass
        # Do cleanup in the "finally" block


def test_true():
    """
    Dummy pytest-style case
    """
    assert True


def test_with_fixture(example_fixture):
    """
    Test using a fixture
    """
    assert example_fixture["hello"] == "world"
