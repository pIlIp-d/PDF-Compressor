from abc import ABC, abstractmethod
from pdfcompressor.compressor.processor import Processor


class Compressor(Processor, ABC):
    def __init__(self, processor: Processor):
        super().__init__(processor)

    @abstractmethod
    def compress(self, source_path: str, destination_path: str) -> None: pass
