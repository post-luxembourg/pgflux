from unittest.mock import Mock

import pgflux.cli as cli  # TODO <- should really be "pgflux.core"
from pgflux.output import HTTPSOutput, Output


def test_http_output():
    mock_output = Mock()
    cli.execute_query("cluster:connections", [], mock_output)
    mock_output.send.assert_called()  # type: ignore


def test_factory():
    instance = Output.create("https")
    assert isinstance(instance, HTTPSOutput)
