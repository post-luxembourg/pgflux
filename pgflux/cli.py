import argparse
import sys
from typing import List, TextIO

from pgflux import core
from pgflux.influx import row_to_influx, send_to_influx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("queries", nargs="*")
    parser.add_argument("--list-queries", action="store_true", default=False)
    return parser.parse_args()


def list_queries(stream: TextIO) -> None:
    list_queries_internal("cluster", stream)
    list_queries_internal("db", stream)


def list_queries_internal(scope: str, stream: TextIO) -> None:
    """
    Print all supported queries into the given stream
    """
    items = sorted(
        core.iter_query_files("cluster"),
        key=lambda row: (row.query_name, row.version),
    )
    header = ("Query Name", "Minimal PG Version")
    query_name_size = len(header[0])
    version_size = len(header[1])
    for row in items:
        query_name_size = max(len(str(row.query_name)), query_name_size)
        version_size = max(len(str(row.version)), version_size)
    row_template = f"│ %-7s │ %-{query_name_size}s │ %{version_size}s │"
    header_str = (
        f"│ Scope   │ %-{query_name_size}s │ %{version_size}s │" % header
    )
    print("─" * len(header_str), file=stream)
    print(header_str, file=stream)
    print("─" * len(header_str), file=stream)
    for item in items:
        print(
            row_template % (scope, item.query_name, item.version), file=stream
        )
    print("─" * len(header_str), file=stream)


def execute_query(query: str, stream: TextIO) -> None:
    queries = core.load_queries()
    with core.connect() as connection:
        result = list(core.execute_global(connection, queries.cluster, query))

    payload: List[str] = []
    for row in result:
        try:
            output = row_to_influx(query, row)
            payload.append(output)
        except core.PgFluxException as exc:
            print(f">> ERROR in {query}: {exc}")  # XXX
    send_to_influx("localhost:8086", "\n".join(payload))


def main() -> int:  # pragma: no cover
    """
    Main CLI entry-point of the script
    """
    args = parse_args()
    if args.list_queries:
        list_queries(sys.stdout)
        return 0
    for query in args.queries:
        execute_query(query, sys.stdout)
    return 0
