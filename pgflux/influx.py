import http.client
import logging
import urllib.parse
from base64 import b64encode
from contextlib import contextmanager
from os import getenv
from typing import Any, Dict, Generator, List, Mapping, Tuple, Union

from dotenv import load_dotenv

from pgflux.core import PgFluxException

LOG = logging.getLogger(__name__)


def with_type(value: Union[int, str, float, bool]) -> str:
    """
    Add an InfluxDB line-protocol type-hint.

    >>> with_type(10)
    '10i'
    >>> with_type("hello")
    'hello'
    """
    if isinstance(value, int):
        return f"{value}i"
    return str(value)


def row_to_influx(
    measurement: str, row: Mapping[str, Any], prefix: str = ""
) -> str:
    """
    Convert db-results from PostgreSQL into a line for InfluxDB line-protocol

    The *row* **must** contain the key 'timestamp' as a unix-timestamp integer
    value.

    When converting, each column name starting with ``tag:`` will be converted
    to an InfluxDB tag, all other columns will be considered an InfluxDB field.

    Example:

    >>> row_to_influx(
    ...     'mymeasurement',
    ...     {'tag:database': 'postgres', 'size': 8758051}
    ... )
    'mymeasurement,database=postgres size=8758051 1234'
    """
    tags: List[str] = []
    fields: List[str] = []
    timestamp: int = 0
    for key, value in row.items():
        if key == "timestamp":
            timestamp = value
            continue
        if key.startswith("tag:"):
            tags.append(f"{key[4:]}={value}")
        else:
            fields.append(f"{key}={with_type(value)}")

    # If the timestamp is still 0, the data did not contain the timestamp value
    # from the DB. It is required so we bail out.
    if timestamp == 0:
        raise PgFluxException("Missing column 'timestamp' in the query.")

    if tags:
        tag_component = "," + ",".join(tags)
    else:
        tag_component = ""
    field_component = ",".join(fields)

    return f"{prefix}{measurement}{tag_component} {field_component} {timestamp}"


@contextmanager
def connect() -> Generator[
    Tuple[http.client.HTTPSConnection, Dict[str, str], Dict[str, str]],
    None,
    None,
]:
    """
    Create a new InfluxDB connection using the ``PGFLUX_INFLUX_*`` environment
    variables.

    The variables are also loaded from a ``.env`` file in the current working
    folder if it exists.
    """
    load_dotenv(".env")
    host = getenv("PGFLUX_INFLUX_HOST", "")
    username = getenv("PGFLUX_INFLUX_USERNAME", "")
    password = getenv("PGFLUX_INFLUX_PASSWORD", "")
    dbname = getenv("PGFLUX_INFLUX_DBNAME", "")
    if not all([host, username, password, dbname]):
        raise PgFluxException("PGFLUX_INFLUX* do not seem to be set.")
    token = b64encode(f"{username}:{password}".encode("ascii")).decode("ascii")
    params = {"db": dbname, "precision": "s"}
    headers = {
        "Content-type": "text/plain",
        "Authorization": f"BASIC {token}",
    }
    conn = http.client.HTTPSConnection(host)
    try:
        yield conn, headers, params
    finally:
        conn.close()


def send_to_influx(
    connection: http.client.HTTPSConnection,
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
    connection.request("POST", f"/write?{params_encoded}", payload, headers)
    response = connection.getresponse()
    return response
