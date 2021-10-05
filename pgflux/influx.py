import http.client
import logging
import urllib.parse
from base64 import b64encode
from contextlib import contextmanager
from os import getenv
from typing import Any, Dict, List, Tuple, Union

from dotenv import load_dotenv

from pgflux.core import PgFluxException

LOG = logging.getLogger(__name__)


def with_type(value: Union[int, str, float, bool]) -> str:
    if isinstance(value, int):
        return f"{value}i"
    return str(value)


def row_to_influx(measurement: str, row: Dict[str, Any], prefix="") -> str:
    """
    Convert db-results from PostgreSQL into a line for InfluxDB line-protocol

    Example:

    >>> row_to_influx(
    ...     'mymeasurement',
    ...     {'tag:database': 'postgres', 'size': 8758051}
    ... )
    'mymeasurement,database=postgres size=8758051 1234'
    """
    tags: List[str] = []
    fields: List[str] = []
    try:
        timestamp: int = int(row.pop("timestamp"))
    except KeyError as exc:
        raise PgFluxException(
            "Missing column 'timestamp' in the query."
        ) from exc
    for key, value in row.items():
        if key.startswith("tag:"):
            tags.append(f"{key[4:]}={value}")
        else:
            fields.append(f"{key}={with_type(value)}")
    if tags:
        tag_component = "," + ",".join(tags)
    else:
        tag_component = ""
    field_component = ",".join(fields)

    return f"{prefix}{measurement}{tag_component} {field_component} {timestamp}"


@contextmanager  # type: ignore
def connect() -> Tuple[
    http.client.HTTPSConnection, Dict[str, str], Dict[str, str]
]:
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
    params_encoded = urllib.parse.urlencode(params)
    connection.request("POST", f"/write?{params_encoded}", payload, headers)
    response = connection.getresponse()
    return response
