import sys
from typing import TextIO

from pgflux.output.interface import Output


class StreamOutput(Output):

    STREAM: TextIO = sys.stdout
    NAME = "stdout"
    CLI_HELP = "Writes all measurements onto stdout"

    def send(self, row: str) -> None:
        print(row, file=self.STREAM)

    def flush(self) -> None:
        pass
