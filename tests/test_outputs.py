from unittest.mock import Mock

import pgflux.core as core
from pgflux.output import HTTPSOutput, Output


def test_http_output():
    mock_output = Mock()
    core.execute_query("cluster:connections", [], mock_output)
    mock_output.send.assert_called()  # type: ignore


def test_factory():
    instance = Output.create("https")
    assert isinstance(instance, HTTPSOutput)
