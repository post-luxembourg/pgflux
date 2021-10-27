from typing import Tuple
from unittest.mock import Mock, patch

import pytest
from psycopg2.extensions import connection as Connection

import pgflux.core as core
import pgflux.output.http as http
from pgflux.enums import Precision
from pgflux.exc import PgFluxException
from pgflux.output import HTTPSOutput, Output


@pytest.fixture
def mock_http_connection() -> Tuple[Mock, http.HTTPOutput]:
    def fake_getenv(key: str, fallback: str) -> str:
        test_data = {
            "PGFLUX_INFLUX_HOST": "fake-host",
            "PGFLUX_INFLUX_USERNAME": "fake-username",
            "PGFLUX_INFLUX_PASSWORD": "fake-password",
            "PGFLUX_INFLUX_DBNAME": "fake-db-name",
        }
        return test_data.get(key, fallback)

    with patch("pgflux.output.http.getenv") as getenv:
        getenv.side_effect = fake_getenv
        instance = http.HTTPOutput()
        instance.CONNECTION_CLASS = Mock()  # type: ignore
        fake_connection = Mock(name="fake-connection")
        instance.CONNECTION_CLASS.return_value = fake_connection
        yield fake_connection, instance  # type: ignore


def test_http_output():
    mock_output = Mock()
    mock_output.PRECISION = Precision.SECONDS
    with core.connect() as db_connection:
        db_connection: Connection
        core.execute_query(
            db_connection, "cluster:connections", [], mock_output
        )
    mock_output.send.assert_called()  # type: ignore


def test_factory():
    instance = Output.create("https")
    assert isinstance(instance, HTTPSOutput)


def test_http_send_to_influx():
    mock_connection = Mock()
    mock_response = Mock(status=204)
    mock_connection.getresponse.return_value = mock_response  # type: ignore
    response = http.send_to_influx(
        mock_connection, {"Foo": "Bar"}, {"frob": "nix"}, "the-payload"
    )
    mock_connection.request.assert_called_with(  # type: ignore
        "POST", "/write?frob=nix", "the-payload", {"Foo": "Bar"}
    )
    assert response is mock_response


def test_http_send_to_influx_error():
    mock_connection = Mock()
    mock_response = Mock(status=500)
    mock_connection.getresponse.return_value = mock_response  # type: ignore
    with pytest.raises(PgFluxException):
        http.send_to_influx(
            mock_connection, {"Foo": "Bar"}, {"frob": "nix"}, "the-payload"
        )


def test_http_connect(mock_http_connection: Tuple[Mock, http.HTTPOutput]):

    fake_connection, http_output = mock_http_connection

    with http_output.connect() as connection:
        conn, headers, params = connection
        assert conn is fake_connection
        assert headers == {
            "Content-Type": "text/plain",
            "Authorization": "BASIC ZmFrZS11c2VybmFtZTpmYWtlLXBhc3N3b3Jk",
        }
        assert params == {
            "db": "fake-db-name",
            "precision": "s",
        }
    fake_connection.close.assert_called()  # type: ignore


def test_http_send_flush(mock_http_connection: Tuple[Mock, http.HTTPOutput]):

    fake_connection, http_output = mock_http_connection
    fake_connection.getresponse.return_value = Mock(status=204)  # type: ignore
    http_output.send("hello-world")
    http_output.send("hello-world2")
    http_output.flush()
    fake_connection.request.assert_called_with(  # type: ignore
        "POST",
        "/write?db=fake-db-name&precision=s",
        "hello-world\nhello-world2",
        {
            "Content-Type": "text/plain",
            "Authorization": "BASIC ZmFrZS11c2VybmFtZTpmYWtlLXBhc3N3b3Jk",
        },
    )
