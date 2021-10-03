import logging
from contextlib import contextmanager
from os import getenv
from pathlib import Path
from typing import Any, Dict, Iterable, NamedTuple

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

LOG = logging.getLogger(__name__)


class PgVersion(NamedTuple):
    major: int
    minor: int


class PgFluxException(Exception):
    """
    Base exception for pgflux
    """


def get_pg_version(cursor: Any) -> PgVersion:
    """
    Returns the posgtes server version as a tuple of integers.

    Example:

    >>> get_pg_version(conn)
    (9, 5, 8)
    """
    # See https://www.postgresql.org/docs/14/libpq-status.html#LIBPQ-PQSERVERVERSION
    cursor.execute("SELECT current_setting('server_version_num')")
    version_num = int(cursor.fetchone()[0])
    if version_num < 100_000:
        major = version_num // 10000
        minor = (version_num % 10000) // 100
    else:
        major = version_num // 10000
        minor = version_num % 10000
    return PgVersion(major, minor)


def load_queries() -> Dict[str, Dict[PgVersion, str]]:
    """
    Load the bundled SQL queries from disk
    """
    here = Path(__file__).parent / "queries"
    output: Dict[str, Dict[PgVersion, str]] = {}
    for container in here.iterdir():
        if not container.is_dir():
            continue
        tmp: Dict[PgVersion, str] = {}
        for query_file in container.glob("*.sql"):
            try:
                major_str, minor_str, _ = query_file.name.split(".")
                version = PgVersion(int(major_str), int(minor_str))
            except ValueError as exc:
                LOG.error("Invalid filename %s (%s)", query_file, exc)
                continue

            tmp[version] = query_file.read_text()
        output[container.name] = tmp
    return output


def get_query(
    queries: Dict[str, Dict[PgVersion, str]],
    query_name: str,
    version: PgVersion,
) -> str:
    """
    Retrieve a query by name targeted at the given postgres version
    """
    if query_name not in queries:
        return ""
    output = ""
    for version_num, query in sorted(queries[query_name].items()):
        if version_num > version:
            break
        output = query
    return output


@contextmanager  # type: ignore
def connect() -> connection:
    load_dotenv(".env")
    dsn = getenv("PGFLUX_DSN", "")
    if not dsn:
        raise PgFluxException("PGFLUX_DSN does not seem to be set.")
    with psycopg2.connect(dsn) as connection:  # type: ignore
        yield connection


def execute(
    connection: Any, queries: Dict[str, Dict[PgVersion, str]], query_name: str
) -> Iterable[Dict[str, Any]]:
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        version = get_pg_version(cursor)
        query = get_query(queries, query_name, version)
        try:
            cursor.execute(query)
        except Exception as exc:
            raise PgFluxException(
                f"Unable to execute query {query_name!r} for PG-version "
                f"{version.major}.{version.minor}"
            ) from exc
        for row in cursor:
            yield dict(row)
