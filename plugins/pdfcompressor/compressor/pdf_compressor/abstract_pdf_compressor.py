import os
from abc import ABC

import fitz

from ...compressor.compressor import Compressor
from ...utility.EventHandler import EventHandler
from ...utility.io_path_parser import IOPathParser
from ...utility.console_utility import ConsoleUtility
from ...utility.os_utility import OsUtility


class AbstractPdfCompressor(Compressor, ABC):
    def __init__(self, event_handlers: list[EventHandler] = list()):
        super().__init__(event_handlers)
        self._final_merge_file = ""

    @staticmethod
    def _get_temp_file(filename: str):
        return os.path.abspath(os.path.join("", "temporary_files", OsUtility.get_filename(filename) + "_temp.pdf"))

    def postprocess(self, source_file: str, destination_file: str) -> None:
        if self._final_merge_file != "":
            # merge new file into pdf (final_merge_file)
            merger = fitz.open()
            if os.path.exists(self._final_merge_file):
                with fitz.open(self._final_merge_file) as f:
                    merger.insert_pdf(f)
            with fitz.open(destination_file) as f:
                merger.insert_pdf(f)
            merger.save(self._final_merge_file)
        super().postprocess(source_file, destination_file)

    def compress(self, source_path, destination_path):
        self._final_merge_file = ""

        io_path_parser = IOPathParser(source_path, destination_path, ".pdf", ".pdf", "_compressed")
        source_file_list = io_path_parser.get_input_file_paths()
        destination_file_list = io_path_parser.get_output_file_paths()

        is_merging = io_path_parser.is_merging()

        # save size for comparison at the end
        orig_sizes = OsUtility.get_filesize_list(source_file_list)

        # create temporary destinations to avoid data loss
        temporary_destination_file_list = [self._get_temp_file(file) for file in destination_file_list]

        if is_merging:
            self._final_merge_file = destination_file_list[0][:-4] + "_merged.pdf"
            destination_file_list = [destination_file_list[0] for _ in range(len(source_file_list))]
            temporary_destination_file_list = [temporary_destination_file_list[0] for _ in range(len(source_file_list))]

        for event_handler in self.event_handlers:
            event_handler.started_processing()

        self.compress_file_list(source_file_list, temporary_destination_file_list)

        if is_merging:
            # move merge result to destination
            OsUtility.move_file(temporary_destination_file_list[0], self._final_merge_file)
            ConsoleUtility.print_green(f"Merged pdfs into {ConsoleUtility.get_file_string(self._final_merge_file)}")

        if is_merging:
            end_size = OsUtility.get_file_size(temporary_destination_file_list[0])
        else:
            end_size = sum(OsUtility.get_filesize_list(temporary_destination_file_list))

        if len(source_file_list) > 1:
            ConsoleUtility.print_stats(sum(orig_sizes), end_size, "All Files")
            ConsoleUtility.print("\n")

        if is_merging:
            OsUtility.move_file(self._final_merge_file, destination_path)
        else:
            for temp_destination, destination in zip(temporary_destination_file_list, destination_file_list):
                OsUtility.move_file(temp_destination, destination)

        for event_handler in self.event_handlers:
            event_handler.finished_all_files()
