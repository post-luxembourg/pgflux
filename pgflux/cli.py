import argparse
import sys
from typing import TextIO

from pgflux import core


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("queries", nargs="*")
    parser.add_argument("--list-queries", action="store_true", default=False)
    return parser.parse_args()


def list_queries(stream: TextIO) -> None:
    """
    Print all supported queries into the given stream
    """
    items = sorted(
        core.iter_query_files(), key=lambda row: (row.query_name, row.version)
    )
    header = ("Query Name", "Minimal PG Version")
    query_name_size = len(header[0])
    version_size = len(header[1])
    for row in items:
        query_name_size = max(len(str(row.query_name)), query_name_size)
        version_size = max(len(str(row.version)), version_size)
    row_template = f"│ %-{query_name_size}s │ %{version_size}s │"
    header_str = f"│ %-{query_name_size}s │ %{version_size}s │" % header
    print(header_str, file=stream)
    print("─" * len(header_str), file=stream)
    for item in items:
        print(row_template % (item.query_name, item.version), file=stream)


def main() -> int:  # pragma: no cover
    """
    Main CLI entry-point of the script
    """
    args = parse_args()
    if args.list_queries:
        list_queries(sys.stdout)
        return 0
    return 0
