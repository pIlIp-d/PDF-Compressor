from abc import ABC, abstractmethod
import os

from plugins.pdfcompressor.processor.processor import Processor
from plugins.pdfcompressor.utility.EventHandler import EventHandler


class Converter(Processor, ABC):
    def __init__(self, origin_path: str, dest_path: str, event_handlers: list[EventHandler] = list()):
        super().__init__(event_handlers)
        self.origin_path = os.path.abspath(origin_path)
        self.dest_path = os.path.abspath(dest_path)

    @abstractmethod
    def convert(self) -> None:
        pass
