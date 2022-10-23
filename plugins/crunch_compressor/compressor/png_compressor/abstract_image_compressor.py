import os
from abc import ABC

from PIL import Image

from django_app.plugin_system.processing_classes.processor import Processor
from django_app.utility.os_utility import OsUtility


class AbstractImageCompressor(Processor, ABC):
    def __init__(
            self,
            file_type_from: str = "png",
            file_type_to: str = "png",
            event_handlers=None,
            run_multi_threaded: bool = True
    ):
        super().__init__(
            event_handlers=event_handlers,
            file_type_from=file_type_from,
            file_type_to=file_type_to,
            processed_part="Pages",  # TODO make parameter
            run_multi_threaded=run_multi_threaded
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

    def _compare_and_use_better_option(self, file_option_1: str, file_option_2: str, destination_file: str) -> None:
        size_option_1 = OsUtility.get_file_size(file_option_1)
        size_option_2 = OsUtility.get_file_size(file_option_2)

        # compression worked -> copy file to final destination
        if self._is_valid_image(file_option_2) and size_option_1 > size_option_2 or \
                not self._is_valid_image(file_option_1):
            OsUtility.copy_file(file_option_2, destination_file)
        # error in output file -> copy source file to destination
        else:
            OsUtility.copy_file(file_option_1, destination_file)
