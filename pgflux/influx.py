import logging
from typing import Any, List, Mapping, Union

from pgflux.exc import PgFluxException

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
            timestamp = int(
                value
            )  # TODO verify if this was not fixed in an earlier change (between 2021-10-10 and 2021-10-17)
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
