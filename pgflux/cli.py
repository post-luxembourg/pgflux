import argparse
import logging
import sys
from typing import Dict, List, Optional, TextIO

from dotenv.main import load_dotenv

from pgflux import core
from pgflux.exc import PgFluxException
from pgflux.influx import row_to_influx
from pgflux.output.interface import Output

LOG = logging.getLogger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "queries",
        nargs="*",
        help=(
            "The query to be run against the PostgreSQL cluster "
            "(can be specified multiple times)"
        ),
    )
    parser.add_argument(
        "--list-queries",
        action="store_true",
        default=False,
        help="List all available PostgreSQL queries by name and exit.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="If this flag is set, run all the available queries.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help=(
            "RegEx of database names that should be excluded from the "
            "statistics. Can be supplied multiple times"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show more output on the console",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="stdout",
        help="Define where the data should be sent to.",
    )
    parser.add_argument(
        "--list-outputs",
        action="store_true",
        default=False,
        help="List all possible outputs",
    )
    return parser.parse_args(args)


def list_outputs(stream: TextIO) -> None:
    """
    List all available output targets.

    :param stream: The target stream where the result will be printed into.
    """
    for name, cls in Output.REGISTRY.items():
        print(
            f"{name}: {getattr(cls, 'CLI_HELP', cls.__name__)}",
            file=stream,
        )
        env_vars = getattr(cls, "ENV_VARS", {})  # type: ignore
        if env_vars:
            print("  Environment variables for configuration:")
        for key, value in env_vars.items():
            print(f"    | {key:<30s}: {value}", file=stream)


def list_queries(stream: TextIO) -> None:
    """
    List all available queries.

    :param stream: The target stream where the result will be printed into.
    """
    list_queries_internal(core.Scope.CLUSTER, stream)
    list_queries_internal(core.Scope.DB, stream)


def list_queries_internal(scope: core.Scope, stream: TextIO) -> None:
    """
    List all available queries with the given scope.

    :param scope: Either database-local or cluster-global
    :param stream: The target stream where the result will be printed into.
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


def execute_query(query: str, exclude: List[str], output: Output) -> None:
    """
    Run the given query against the DB clusters excluding any databases where
    the name matches any regex in *exclude*.

    :param query: The *name* of the query to execute
    :param exclude: A list of regexes which are all used to verify if a database
        should be excluded from the stats. If *any* one of them matches, the DB
        is skipped.
    """
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
                        connection, queries.db, query_name, dbname
                    )
                )
        else:
            raise PgFluxException(f"Unknown scope: {scope}")

    for row in result:
        try:
            tmp = row_to_influx(query_name, row, prefix="postgres_")
            output.send(tmp)
        except PgFluxException as exc:
            LOG.error("ERROR in %s: %s", query_name, exc)
    output.flush()


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
    load_dotenv(".env")
    args = parse_args()

    if args.list_queries:
        list_queries(sys.stdout)
        return 0

    if args.list_outputs:
        list_outputs(sys.stdout)
        return 0

    setup_logging(args.verbose)
    LOG.debug("Startup")

    output = Output.create(args.output)

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
            execute_query(query, args.exclude, output)
        LOG.debug("Done")
    else:
        for query in args.queries:
            execute_query(query, args.exclude, output)
        LOG.debug("Done")
    return 0
