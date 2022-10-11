import inspect
from abc import ABC, abstractmethod
from functools import wraps


class Postprocessor(ABC):
    @abstractmethod
    def postprocess(self, source_file: str, destination_file: str) -> None: pass
