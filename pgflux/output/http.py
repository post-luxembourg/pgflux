import http.client
import logging
import urllib.parse
from base64 import b64encode
from contextlib import contextmanager
from os import getenv
from typing import Dict, Generator, List, Tuple

from pgflux.core import PgFluxException
from pgflux.enums import Precision
from pgflux.output.interface import Output

LOG = logging.getLogger(__name__)


def send_to_influx(
    connection: http.client.HTTPConnection,
    headers: Dict[str, str],
    params: Dict[str, str],
    payload: str,
) -> http.client.HTTPResponse:
    """
    Send the data in *payload* to InfluxDB using *connection*.

    This sends a simple HTTP POST request to the other end of *connection*.

    :param connection: The HTTP connection to the InfluxDB endpoint
    :param headers: An optional mapping for HTTP headers
    :param param: An optional mapping for HTTP query arguments
    :param payload: The data to send
    :return: A HTTP response
    """
    params_encoded = urllib.parse.urlencode(params)
    method = "POST"
    url = f"/write?{params_encoded}"
    connection.request(method, url, payload, headers)
    response = connection.getresponse()
    LOG.debug(
        "HTTP %s %s (%d bytes) -> %r %s",
        method,
        url,
        len(payload),
        response.status,
        response.reason,
    )
    if response.status >= 400:
        raise PgFluxException(
            f"Unable to send data to InfluxDB ({response.read()})"
        )
    return response


class HTTPOutput(Output):

    CONNECTION_CLASS = http.client.HTTPConnection
    NAME = "http"
    CLI_HELP = "Sends a bulk HTTP POST request to InfluxDB"
    ENV_VARS = {
        "PGFLUX_INFLUX_HOST": "Hostname of the InfluxDB",
        "PGFLUX_INFLUX_DBNAME": "The database name",
        "PGFLUX_INFLUX_USERNAME": "The username",
        "PGFLUX_INFLUX_PASSWORD": "The password",
    }
    PRECISION = Precision.SECONDS

    def __init__(self) -> None:
        super().__init__()
        self.lines: List[str] = []

    @contextmanager
    def connect(
        self,
    ) -> Generator[
        Tuple[http.client.HTTPConnection, Dict[str, str], Dict[str, str]],
        None,
        None,
    ]:
        """
        Create a new InfluxDB connection using the ``PGFLUX_INFLUX_*`` environment
        variables.

        The variables are also loaded from a ``.env`` file in the current working
        folder if it exists.
        """
        host = getenv("PGFLUX_INFLUX_HOST", "")
        username = getenv("PGFLUX_INFLUX_USERNAME", "")
        password = getenv("PGFLUX_INFLUX_PASSWORD", "")
        dbname = getenv("PGFLUX_INFLUX_DBNAME", "")

        headers = {
            "Content-Type": "text/plain",
        }

        if username and password:
            token = b64encode(f"{username}:{password}".encode("ascii")).decode(
                "ascii"
            )
            headers["Authorization"] = f"BASIC {token}"

        if not all([host, dbname]):
            raise PgFluxException("PGFLUX_INFLUX* do not seem to be set.")

        params = {"db": dbname, "precision": "s"}
        conn = self.CONNECTION_CLASS(host)
        try:
            yield conn, headers, params
        finally:
            conn.close()

    def send(self, row: str) -> None:
        return self.lines.append(row)

    def flush(self) -> None:
        with self.connect() as influx_meta:
            connection, headers, params = influx_meta
            send_to_influx(connection, headers, params, "\n".join(self.lines))
        self.lines.clear()


class HTTPSOutput(HTTPOutput):
    CONNECTION_CLASS = http.client.HTTPSConnection
    NAME = "https"
