import logging
from pathlib import Path
from typing import Any, Dict, NamedTuple

LOG = logging.getLogger(__name__)


class PgVersion(NamedTuple):
    major: int
    minor: int


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
