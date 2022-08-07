from abc import ABC
from typing import Type, TypeVar

# generic Type to assure only processors of type Processor are passed as parameters
TProcessor = TypeVar("TProcessor", bound="Processor")


class Processor(ABC):
    def __init__(self, processor: TProcessor = None):
        self._processors = [processor] if processor is not None else []

    def preprocess(self, source: str, destination: str) -> None:
        for processor in self._processors:
            processor.preprocess(source, destination)

    def postprocess(self, source: str, destination: str) -> None:
        for processor in self._processors:
            processor.postprocess(source, destination)

    def add_processor(self, processor: TProcessor):
        self._processors.append(processor)

    def clear_processors(self):
        self._processors = []
