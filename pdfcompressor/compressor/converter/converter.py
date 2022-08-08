from abc import ABC, abstractmethod
import os

from pdfcompressor.processor.processor import Processor


class Converter(Processor, ABC):
    def __init__(self, origin_path: str, dest_path: str):
        super().__init__()
        self.origin_path = os.path.abspath(origin_path)
        self.dest_path = os.path.abspath(dest_path)

    @abstractmethod
    def convert(self) -> None:
        pass
