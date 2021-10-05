import http.client
import logging
import urllib.parse
from typing import Any, Dict, List, Union

from pgflux.core import PgFluxException

LOG = logging.getLogger(__name__)


def with_type(value: Union[int, str, float, bool]) -> str:
    if isinstance(value, int):
        return f"{value}i"
    return str(value)


def row_to_influx(measurement: str, row: Dict[str, Any]) -> str:
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

    return f"{measurement}{tag_component} {field_component} {timestamp}"


def send_to_influx(host: str, payload: str) -> None:
    params = urllib.parse.urlencode({"db": "postgres_stats"})
    headers = {"Content-type": "text/plain"}
    conn = http.client.HTTPConnection(host)
    conn.request("POST", f"/write?{params}", payload, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    print(response.read())
    conn.close()
