import argparse
import logging
import sys
from typing import Dict, List, TextIO

from pgflux import core
from pgflux.influx import connect, row_to_influx, send_to_influx

LOG = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("queries", nargs="*")
    parser.add_argument("--list-queries", action="store_true", default=False)
    parser.add_argument("--all", action="store_true", default=False)
    parser.add_argument("--exclude", action="append")
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    return parser.parse_args()


def list_queries(stream: TextIO) -> None:
    list_queries_internal(core.Scope.CLUSTER, stream)
    list_queries_internal(core.Scope.DB, stream)


def list_queries_internal(scope: core.Scope, stream: TextIO) -> None:
    """
    Print all supported queries into the given stream
    """
    items = sorted(
        core.iter_query_files(scope),
        key=lambda row: (row.query_name, row.version),
    )
    header = ("Query Name", "Minimal PG Version")
    query_name_size = len(header[0])
    version_size = len(header[1])
    for row in items:
        query_name_size = max(
            len(scope.value + str(row.query_name)) + 1, query_name_size
        )
        version_size = max(len(str(row.version)), version_size)
    row_template = f"│ %-{query_name_size}s │ %{version_size}s │"
    header_str = f"│ %-{query_name_size}s │ %{version_size}s │" % header
    print("─" * len(header_str), file=stream)
    print(header_str, file=stream)
    print("─" * len(header_str), file=stream)
    for item in items:
        print(
            row_template % (f"{scope.value}:{item.query_name}", item.version),
            file=stream,
        )
    print("─" * len(header_str), file=stream)


def execute_query(query: str, exclude: List[str], stream: TextIO) -> None:
    scope_str, _, query_name = query.partition(":")
    scope = core.Scope(scope_str)
    queries = core.load_queries()
    result: List[Dict[str, str]] = []
    with core.connect() as connection:
        if scope == core.Scope.CLUSTER:
            result.extend(
                core.execute_global(connection, queries.cluster, query_name)
            )
        elif scope == core.Scope.DB:
            for dbname in core.list_databases(connection, exclude):
                result.extend(
                    core.execute_local(
                        connection, queries.db, dbname, query_name
                    )
                )
        else:
            raise core.PgFluxException(f"Unknown scope: {scope}")

    payload: List[str] = []
    for row in result:
        try:
            output = row_to_influx(query_name, row, prefix="postgres_")
            payload.append(output)
        except core.PgFluxException as exc:
            LOG.error("ERROR in %s: %s", query_name, exc)
    with connect() as influx_meta:
        connection, headers, params = influx_meta
        send_to_influx(connection, headers, params, "\n".join(payload))


def setup_logging(is_verbose: bool = False) -> None:
    """
    Enables logging if *is_verbose* is true. Otherwise this is a no-op.
    """
    if not is_verbose:
        return
    format = "%(asctime)-15s | %(levelname)-8s | %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format)


def main() -> int:  # pragma: no cover
    """
    Main CLI entry-point of the script
    """
    args = parse_args()
    if args.list_queries:
        list_queries(sys.stdout)
        return 0
    setup_logging(args.verbose)
    LOG.debug("Startup")
    if args.all:
        queries = {
            f"{core.Scope.CLUSTER.value}:{query.query_name}"
            for query in core.iter_query_files(core.Scope.CLUSTER)
        }
        queries |= {
            f"{core.Scope.DB.value}:{query.query_name}"
            for query in core.iter_query_files(core.Scope.DB)
        }
        for query in queries:
            execute_query(query, args.exclude, sys.stdout)
        LOG.debug("Done")
    else:
        for query in args.queries:
            execute_query(query, args.exclude, sys.stdout)
        LOG.debug("Done")
    return 0
