import os
from abc import ABC
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar
import inspect
from functools import wraps

# generic Type to assure only processors of type Processor are passed as parameters
from pdfcompressor.processor.postprocessor import Postprocessor
from pdfcompressor.processor.preprocessor import Preprocessor

TProcessor = TypeVar("TProcessor", bound="Processor")


class Processor(Postprocessor, Preprocessor, ABC):
    def __init__(self):
        self._preprocessors = []
        self._postprocessors = []

    def add_preprocessor(self, processor: Preprocessor):
        self._preprocessors.append(processor)

    def add_postprocessor(self, processor: Postprocessor):
        self._postprocessors.append(processor)

    def clear_processors(self):
        self._preprocessors = []
        self._postprocessors = []

    def preprocess(self, source_file: str, destination_file: str) -> None:
        for processor in self._preprocessors:
            processor.preprocess(source_file, destination_file)

    def postprocess(self, source_file: str, destination_file: str) -> None:
        for processor in self._postprocessors:
            processor.postprocess(source_file, destination_file)

    @staticmethod
    def _custom_map_execute(method, args_list: list):
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            tasks = []
            for method_parameter in args_list:
                tasks.append(executor.submit(method, **method_parameter))
            # waits for all jobs to be completed
            for _ in as_completed(tasks):
                pass

    @staticmethod
    def pre_and_post_processed(f):
        # decorator executes preprocess before and postprocess after method call
        @wraps(f)
        def wrapper(self, *args, **kw):
            if hasattr(self, 'preprocess') and inspect.ismethod(self.preprocess):
                self.preprocess(args[0], args[1])
            result = f(self, *args, **kw)
            if hasattr(self, 'postprocess') and inspect.ismethod(self.postprocess):
                self.postprocess(args[0], args[1])
            return result
        return wrapper
