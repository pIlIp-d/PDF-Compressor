from abc import ABC
from concurrent.futures import ProcessPoolExecutor
import inspect
from functools import wraps

# generic Type to assure only processors of type Processor are passed as parameters
from plugins.pdfcompressor.processor.postprocessor import Postprocessor
from plugins.pdfcompressor.processor.preprocessor import Preprocessor
from plugins.pdfcompressor.utility.EventHandler import EventHandler


class Processor(Postprocessor, Preprocessor, ABC):
    def __init__(self, event_handlers: list[EventHandler]):
        self.event_handlers = event_handlers
        self._preprocessors = []
        self._postprocessors = []
        self._add_event_handler_processors()

    def _add_event_handler_processors(self) -> None:
        for event_handler in self.event_handlers:
            self.add_preprocessor(event_handler)
        for event_handler in self.event_handlers:
            self.add_postprocessor(event_handler)

    def add_preprocessor(self, processor: Preprocessor) -> None:
        self._preprocessors.append(processor)

    def add_postprocessor(self, processor: Postprocessor) -> None:
        self._postprocessors.append(processor)

    def clear_processors(self) -> None:
        self._preprocessors = []
        self._postprocessors = []

    def preprocess(self, source_file: str, destination_file: str) -> None:
        for processor in self._preprocessors:
            processor.preprocess(source_file, destination_file)

    def postprocess(self, source_file: str, destination_file: str) -> None:
        for processor in self._postprocessors:
            processor.postprocess(source_file, destination_file)

    @classmethod
    def _custom_map_execute(cls, method, args_list: list, cpu_count: int) -> None:
        with ProcessPoolExecutor(max_workers=cpu_count) as executor:
            for method_parameter in args_list:
                executor.submit(method, **method_parameter)

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
