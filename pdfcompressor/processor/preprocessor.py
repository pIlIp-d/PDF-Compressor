import inspect
from abc import ABC, abstractmethod
from functools import wraps
from decorator import decorator

class Preprocessor(ABC):
    @abstractmethod
    def preprocess(self, source_file: str, destination_file: str) -> None: pass

    @staticmethod
    def super_preprocessed(f):
        @wraps(f)
        def wrapper(self, source_file: str, destination_file: str, *args, **kw):
            if hasattr(self, 'super') and hasattr(self.super(), 'preprocess') and inspect.ismethod(self.super().preprocess):
                self.super().preprocess(args[0], args[1])
            return f(self, source_file, destination_file, *args, **kw)
        return wrapper