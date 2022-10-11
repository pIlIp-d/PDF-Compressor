from abc import ABC

from plugins.crunch_compressor.compressor.png_compressor.abstract_image_compressor import AbstractImageCompressor
from plugins.crunch_compressor.utility.EventHandler import EventHandler


class AbstractPngCompressor(AbstractImageCompressor, ABC):
    def __init__(
            self,
            event_handlers: list[EventHandler] = list()
    ):
        super().__init__(
            event_handlers=event_handlers,
            file_type_from="png",
            file_type_to="png",
        )
