from io import StringIO

import pytest

import pgflux.cli as cli
from pgflux.output import Output


@pytest.mark.parametrize("argvalue", Output.REGISTRY.keys())
def test_output_arg(argvalue: str):
    result = cli.parse_args(["-o", argvalue])
    assert result.output == argvalue
    result = cli.parse_args(["--output", argvalue])
    assert result.output == argvalue


@pytest.mark.parametrize("output_name", Output.REGISTRY.keys())
def test_list_outputs(output_name: str):
    """
    Ensure that we can list our outputs
    """
    stream = StringIO()
    cli.list_outputs(stream)
    assert "PGFLUX_INFLUX_HOST" in stream.getvalue()
    assert output_name in stream.getvalue()


def test_list_queries():
    """
    Ensure that we can list our queries
    """
    stream = StringIO()
    cli.list_queries(stream)
    assert "cluster:connections" in stream.getvalue()
    assert "db:disk_io" in stream.getvalue()
