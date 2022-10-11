import os
from abc import ABC

from PIL import Image

from ..compressor import Compressor
from ...utility.EventHandler import EventHandler


class AbstractImageCompressor(Compressor, ABC):
    def __init__(
            self,
            file_type_from: str = "png",
            file_type_to: str = "png",
            event_handlers: list[EventHandler] = list()
    ):
        super().__init__(
            event_handlers=event_handlers,
            file_type_from=file_type_from,
            file_type_to=file_type_to,
            processed_part="Pages",
        )

    @staticmethod
    def _is_valid_image(path: str) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except:
            # couldn't open and verify -> not a valid image
            return False

    def compress_file_list(self, source_files: list, destination_files: list) -> None:
        self.compress_file_list_multi_threaded(
            source_files,
            destination_files,
            # use all cores, but after 8 it splits bigger tasks -> only 4 each
            os.cpu_count() if os.cpu_count() < 8 else 4
        )
