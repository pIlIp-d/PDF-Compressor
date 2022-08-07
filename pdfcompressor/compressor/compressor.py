from abc import ABC, abstractmethod

from ..processor import Processor


class Compressor(ABC, Processor):
    @abstractmethod
    def compress(self, source_path: str, destination_path: str) -> None: pass
