import inspect
from abc import ABC, abstractmethod
from functools import wraps


class Preprocessor(ABC):
    def preprocess(self, source_file: str, destination_file: str) -> None: pass
