import logging
import re
from contextlib import contextmanager
from copy import copy
from dataclasses import dataclass
from enum import Enum
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, NamedTuple

import psycopg2
from psycopg2.errors import OperationalError
from psycopg2.extensions import connection as Connection
from psycopg2.extras import DictCursor

from pgflux.exc import PgFluxException
from pgflux.influx import row_to_influx

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pgflux.output import Output


class PgVersion(NamedTuple):
    """
    A simple data-type to represent the detected PostgreSQL version.
    """

    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


class Scope(Enum):
    """
    The possible scopes for queries
    """

    #: "cluster" contains all queries which can be run against the whole cluster
    CLUSTER = "cluster"
    #: "db" contains all queries which have to be run against a specific
    #: connection
    DB = "db"


@dataclass
class FileItem:
    """
    A FileItem represents a reference to a SQL file containing a query that can
    be run against a specific PostgreSQL version (including whether it's
    cluster-global or db-local)
    """

    #: The detected PostgreSQL version
    version: PgVersion
    #: The name of the query contained in the file
    query_name: str
    #: The path of the SQL file
    path: Path
    #: Whether the query is cluster-global or db-local
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

    :param scope: Only return queries from the given scope.
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

    :param version: The detected PostgreSQL version
    :param scope: Whether the query is cluster-global or db-local
    :param query_name: The name of the query to look-up
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
    Retrieve a query from a collection of queries by name targeted at the given
    postgres version
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
def connect() -> Connection:
    """
    Create a new database connection using the ``PGFLUX_POSTGRES_DSN``
    environment variable.

    The variable is also loaded from a ``.env`` file in the current working
    folder if it exists.
    """
    dsn = getenv("PGFLUX_POSTGRES_DSN", "")

    if not dsn:
        raise PgFluxException("PGFLUX_POSTGRES_DSN does not seem to be set.")
    with psycopg2.connect(dsn) as connection:  # type: ignore
        yield connection


def execute_global(
    connection: Any, queries: Dict[str, Dict[PgVersion, str]], query_name: str
) -> Iterable[Dict[str, Any]]:
    """
    Execute a query (by name) against the database cluster and return all rows.

    :param connection: A reference to the DB cluster
    :param queries: A collection of queries
    :param query_name: The name of the query to execute
    :return: An iterable over the rows (columns depend on the executed query)
    """
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
            yield with_server_metadata(connection, dict(row))


def execute_local(
    connection: Any,
    queries: Dict[str, Dict[PgVersion, str]],
    query_name: str,
    dbname: str,
) -> Iterable[Dict[str, Any]]:
    """
    Execute a query (by name) against the database cluster and return all rows.

    :param connection: A reference to the DB cluster
    :param queries: A collection of queries
    :param query_name: The name of the query to execute
    :param dbname: The name of the database to connect to
    :return: An iterable over the rows (columns depend on the executed query)
    """
    params = copy(connection.info.dsn_parameters)
    params["password"] = connection.info.password
    params["dbname"] = dbname
    try:
        with psycopg2.connect(**params) as local_connection:  # type: ignore
            with local_connection.cursor(cursor_factory=DictCursor) as cursor:  # type: ignore
                version = get_pg_version(cursor)
                query = get_query(queries, query_name, version)
                if not query:
                    raise PgFluxException(
                        f"Unable to load query {query_name!r} "
                        f"in version {version}"
                    )
                cursor.execute(query)  # type: ignore
                for row in cursor:  # type: ignore
                    yield with_server_metadata(local_connection, row, dbname)
    except OperationalError:  # type: ignore
        LOG.error("Unable to connect to %s", dbname, exc_info=True)


def with_server_metadata(
    connection: Any, row: Mapping[str, Any], dbname: str = ""
) -> Dict[str, str]:
    """
    Enrich a database row with server-metadata.

    This will add the following columns to the data in *row*:

    * tag:dbname
    * tag:server_version_num
    * tag:server_port
    * tag:host
    """
    params = copy(connection.info.dsn_parameters)
    with connection.cursor() as cursor:
        cursor.execute("SHOW server_version")
        cursor.execute("SHOW server_version_num")
        server_version_num = cursor.fetchone()[0]
        cursor.execute("SHOW port")
        port = cursor.fetchone()[0]
    output: Dict[str, Any] = dict(row)  # type: ignore
    if dbname:
        output["tag:dbname"] = dbname
    output["tag:server_version_num"] = server_version_num
    output["tag:server_port"] = port
    if "host" in params:
        output["tag:host"] = params["host"]
    return output


def is_excluded(name: str, pattern: str) -> bool:
    """
    Determine whether the value in *name* matches the reges in *pattern*.

    If True, also emit a log-message.
    """
    if bool(re.fullmatch(pattern, name)):
        LOG.debug("%r was excluded by pattern %r", name, pattern)
        return True
    return False


def list_databases(connection: Any, exclude: List[str]) -> Iterable[str]:
    """
    Return a collection of all database names in the cluster connected to by
    *connection*.

    :param connection: A connection to the DB cluster
    :param exclude: A list of regexes containing exclusion regexes which are
        checked against the DB-names.
    """
    query = (
        'SELECT datname as "database" '
        "FROM pg_database WHERE datistemplate=false;"
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        for (row,) in cursor:
            exclusion_matches = [is_excluded(row, item) for item in exclude]
            if any(exclusion_matches):
                continue
            yield row


def execute_query(
    connection: Connection, query: str, exclude: List[str], output: "Output"
) -> None:
    """
    Run the given query against the DB clusters excluding any databases where
    the name matches any regex in *exclude*.

    :param query: The *name* of the query to execute
    :param exclude: A list of regexes which are all used to verify if a database
        should be excluded from the stats. If *any* one of them matches, the DB
        is skipped.
    """
    scope_str, _, query_name = query.partition(":")
    scope = Scope(scope_str)
    queries = load_queries()
    result: List[Dict[str, str]] = []

    if scope == Scope.CLUSTER:
        result.extend(execute_global(connection, queries.cluster, query_name))
    elif scope == Scope.DB:
        for dbname in list_databases(connection, exclude):
            result.extend(
                execute_local(connection, queries.db, query_name, dbname)
            )
    else:
        raise PgFluxException(f"Unknown scope: {scope}")

    for row in result:
        try:
            tmp = row_to_influx(
                query_name, row, prefix="postgres_", precision=output.PRECISION
            )
            output.send(tmp)
        except PgFluxException as exc:
            LOG.error("ERROR in %s: %s", query_name, exc)
    output.flush()
