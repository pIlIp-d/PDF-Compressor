import os
from abc import ABC

from PIL import Image

from ..compressor import Compressor
from ...utility.EventHandler import EventHandler
from ...utility.io_path_parser import IOPathParser
from ...utility.console_utility import ConsoleUtility
from ...utility.os_utility import OsUtility


class AbstractImageCompressor(Compressor, ABC):
    def __init__(
            self,
            file_type_from: str = ".png",
            file_type_to: str = ".png",
            event_handlers: list[EventHandler] = list()
    ):
        super().__init__(event_handlers)
        self._file_type_from = file_type_from
        self._file_type_to = file_type_to

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

    def postprocess(self, source_file: str, destination_file: str) -> None:
        super().postprocess(source_file, destination_file)

    def compress(self, source_path: str, destination_path: str) -> None:
        io_path_parser = IOPathParser(
            source_path,
            destination_path,
            self._file_type_from,
            self._file_type_to, "_compressed"
        )
        source_file_list = io_path_parser.get_input_file_paths()
        destination_file_list = io_path_parser.get_output_file_paths()

        if io_path_parser.is_merging():
            raise ValueError("Merging from folder into image file is not supported.")

        orig_sizes = OsUtility.get_filesize_list(source_file_list)

        for event_handler in self.event_handlers:
            event_handler.started_processing()

        self.compress_file_list(source_file_list, destination_file_list)

        end_size = sum(OsUtility.get_filesize_list(destination_file_list))
        ConsoleUtility.print_stats(sum(orig_sizes), end_size, "Pages")

        for event_handler in self.event_handlers:
            event_handler.finished_all_files()
