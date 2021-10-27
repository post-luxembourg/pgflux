import argparse
import logging
import sys
from typing import List, Optional, Set, TextIO

from dotenv.main import load_dotenv
from psycopg2.extensions import connection as Connection

from pgflux import core
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


def setup_logging(is_verbose: bool = False) -> None:  # pragma: no cover
    """
    Enables logging if *is_verbose* is true. Otherwise this is a no-op.
    """
    if not is_verbose:
        return
    format = "%(asctime)-15s | %(levelname)-8s | %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format)


def run_queries(
    connection: Connection,
    queries: Set[str],
    all_queries: bool,
    exclude_pattern: List[str],
    output: Output,
):
    if all_queries:
        queries = {
            f"{core.Scope.CLUSTER.value}:{query.query_name}"
            for query in core.iter_query_files(core.Scope.CLUSTER)
        }
        queries |= {
            f"{core.Scope.DB.value}:{query.query_name}"
            for query in core.iter_query_files(core.Scope.DB)
        }
        for query in queries:
            core.execute_query(connection, query, exclude_pattern, output)
        LOG.debug("Done")
    else:
        for query in queries:
            core.execute_query(connection, query, exclude_pattern, output)
        LOG.debug("Done")


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

    with core.connect() as connection:
        run_queries(
            connection,  # type: ignore
            set(args.queries),
            args.all,
            args.exclude,
            output,
        )
    return 0
