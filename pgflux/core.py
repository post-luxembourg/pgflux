import logging
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
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

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


class Scope(Enum):
    CLUSTER = "cluster"
    DB = "db"


@dataclass
class FileItem:
    version: PgVersion
    query_name: str
    path: Path
    scope: Scope


@dataclass
class QueryCollection:
    """
    A collection of queries to run against either the whole DB cluster, or a
    specific DB.

    Some queries return statistics relative to the active client-connection.
    Others report values of the whole cluster and can be run from any
    connection.
    """

    #: Queries to be run against the whole cluster
    cluster: Dict[str, Dict[PgVersion, str]]

    #: Queries to be run against a single DB
    db: Dict[str, Dict[PgVersion, str]]


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


def iter_query_files(scope: Scope) -> Iterable[FileItem]:
    """
    Iterate over all defined query files.
    """
    here = Path(__file__).parent / "queries"
    for container in (here / scope.value).iterdir():
        if not container.is_dir():
            continue
        for query_file in container.glob("*.sql"):
            try:
                major_str, minor_str, _ = query_file.name.split(".")
                version = PgVersion(int(major_str), int(minor_str))
            except ValueError as exc:
                LOG.error("Invalid filename %s (%s)", query_file, exc)
                continue
            yield FileItem(
                version, container.name, query_file.absolute(), scope
            )


def load_queries() -> QueryCollection:
    """
    Load the bundled SQL queries from disk
    """
    output_cluster: Dict[str, Dict[PgVersion, str]] = {}
    output_db: Dict[str, Dict[PgVersion, str]] = {}
    for item in iter_query_files(Scope.CLUSTER):
        tmp: Dict[PgVersion, str] = output_cluster.setdefault(
            item.query_name, {}
        )
        tmp[item.version] = item.path.read_text()
    for item in iter_query_files(Scope.DB):
        tmp: Dict[PgVersion, str] = output_db.setdefault(item.query_name, {})
        tmp[item.version] = item.path.read_text()
    return QueryCollection(output_cluster, output_db)


def get_query_filename(
    version: PgVersion, scope: Scope, query_name: str
) -> str:
    """
    Retrieve the filename where the query for *query_name* was defined.
    """
    items = sorted(
        iter_query_files(scope), key=lambda row: (row.query_name, row.version)
    )
    target = None
    for item in items:
        if item.query_name != query_name:
            continue
        if item.version > version:
            break
        target = item.path
    if not target:
        raise PgFluxException(
            f"Unable to find a file for query {query_name!r} "
            f"in version {version.major}.{version.minor}"
        )

    return str(target.absolute())


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


def execute_global(
    connection: Any, queries: Dict[str, Dict[PgVersion, str]], query_name: str
) -> Iterable[Dict[str, Any]]:
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        version = get_pg_version(cursor)
        query = get_query(queries, query_name, version)
        if not query:
            raise PgFluxException(
                f"Unable to load query {query_name!r} in version {version}"
            )
        try:
            cursor.execute(query)
        except Exception as exc:
            filename = get_query_filename(version, Scope.CLUSTER, query_name)
            raise PgFluxException(
                f"Unable to execute query {query_name!r} from {filename!r}"
            ) from exc
        for row in cursor:
            yield dict(row)


def execute_local(
    connection: Any,
    queries: Dict[str, Dict[PgVersion, str]],
    dbname: str,
    query_name: str,
) -> Iterable[Dict[str, Any]]:
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        version = get_pg_version(cursor)
        query = get_query(queries, query_name, version)
        if not query:
            raise PgFluxException(
                f"Unable to load query {query_name!r} in version {version}"
            )
        cursor.execute(query)
        for row in cursor:
            yield dict(row)


def list_databases(connection: Any) -> Iterable[str]:
    query = (
        'SELECT datname as "database" '
        "FROM pg_database WHERE datistemplate=false;"
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        for (row,) in cursor:
            yield row
