import inspect
from abc import ABC, abstractmethod
from functools import wraps


class Postprocessor(ABC):
    @abstractmethod
    def postprocess(self, source_file: str, destination_file: str) -> None: pass

    @staticmethod
    def super_postprocessed(f):
        @wraps(f)
        def wrapper(self, *args, **kw):
            result = f(self, *args, **kw)
            if hasattr(self, 'super') and hasattr(self.super(), 'postprocess') and inspect.ismethod(
                    self.super().postprocess):
                self.super().postprocess(args[0], args[1])
            return result
        return wrapper
