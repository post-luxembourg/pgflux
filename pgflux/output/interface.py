from abc import ABC, abstractmethod
from typing import Dict, Type

from pgflux.enums import Precision
from pgflux.exc import PgFluxException


class Output(ABC):

    REGISTRY: Dict[str, Type["Output"]] = {}
    PRECISION: Precision = Precision.NANO_SECONDS

    @abstractmethod
    def send(self, row: str) -> None:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def flush(self) -> None:
        raise NotImplementedError("Not yet implemented")

    @staticmethod
    def create(output_name: str) -> "Output":
        result = Output.REGISTRY.get(output_name)
        if not result:
            raise PgFluxException(f"No output found with name {output_name!r}.")
        return result()

    def __init_subclass__(cls) -> None:
        name = getattr(cls, "NAME", "")
        if not name:
            return
        Output.REGISTRY[name] = cls
