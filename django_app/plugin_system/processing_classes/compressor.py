from abc import ABC

from django_app.plugin_system.processing_classes.processor import Processor
from plugins.crunch_compressor.utility.EventHandler import EventHandler


class Compressor(Processor, ABC):

    def __init__(
            self,
            event_handlers: list[EventHandler],
            file_type_from: str,
            file_type_to: str,
            can_merge: bool = False,
            processed_part: str = "All Files"
    ):
        super().__init__(
            event_handlers,
            file_type_from,
            file_type_to,
            "_compressed",  # predefine file appendix
            can_merge,
            processed_part
        )
