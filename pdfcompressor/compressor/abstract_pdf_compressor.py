import os
from abc import ABC, abstractmethod

import fitz

from pdfcompressor.compressor.compressor import Compressor
from pdfcompressor.compressor.processor import Processor
from pdfcompressor.io_path_parser import IOPathParser
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility


class AbstractPdfCompressor(Compressor, Processor, ABC):
    def __init__(self, processor: Processor = None):
        super().__init__(processor)
        self._final_merge_file = ""
        self._supress_stats = False

    @abstractmethod
    def compress_file(self, file: str, destination_file: str) -> None: pass

    @staticmethod
    def _get_temp_file(filename: str):
        return os.path.abspath(os.path.join(".", "temporary_files", OsUtility.get_filename(filename) + "_temp.pdf"))

    def supress_stats(self):
        self._supress_stats = True

    def activate_stats(self):
        self._supress_stats = False

    def postprocess(self, source: str, destination: str) -> None:
        if self._final_merge_file != "":
            # merge new file into pdf (final_merge_file)
            merger = fitz.open()
            if os.path.exists(self._final_merge_file):
                with fitz.open(self._final_merge_file) as f:
                    merger.insert_pdf(f)
            with fitz.open(destination) as f:
                merger.insert_pdf(f)
            merger.save(self._final_merge_file)

        super().postprocess(source, destination)

    @staticmethod
    def __get_filesize_list(file_list: list) -> list:
        return [OsUtility.get_file_size(file) for file in file_list]

    def compress(self, source_path, destination_path):
        self._final_merge_file = ""

        io_path_parser = IOPathParser(source_path, destination_path, ".pdf", ".pdf", "_compressed")
        source_file_list = io_path_parser.get_input_file_paths()
        destination_file_list = io_path_parser.get_output_file_paths()

        is_merging = io_path_parser.is_merging()

        # save size for comparison at the end
        orig_sizes = self.__get_filesize_list(source_file_list)

        # create temporary destinations to avoid data loss
        temporary_destination_file_list = [self._get_temp_file(file) for file in destination_file_list]

        if is_merging:
            self._final_merge_file = destination_file_list[0][:-4] + "_merged.pdf"
            destination_file_list = [destination_file_list[0] for _ in range(len(source_file_list))]
            temporary_destination_file_list = [temporary_destination_file_list[0] for _ in range(len(source_file_list))]

        for file, destination in zip(source_file_list, temporary_destination_file_list):
            self.preprocess(file, destination)
            self.compress_file(file, destination)
            self.postprocess(file, destination)

        if is_merging:
            # move merge result to destination
            OsUtility.move_file(self._final_merge_file, temporary_destination_file_list[0])
            ConsoleUtility.print(
                f"{ConsoleUtility.GREEN}Merged pdfs into{ConsoleUtility.END} " \
                + ConsoleUtility.get_file_string(destination_file_list[0])
            )

        if not self._supress_stats:
            if is_merging:
                end_size = OsUtility.get_file_size(temporary_destination_file_list[0])
            else:
                end_size = sum(self.__get_filesize_list((temporary_destination_file_list)))
            ConsoleUtility.print_stats(sum(orig_sizes), end_size, False)

        if is_merging:
            OsUtility.move_file(temporary_destination_file_list[0], destination_file_list[0])
        else:
            for temp_destination, destination in zip(temporary_destination_file_list, destination_file_list):
                OsUtility.move_file(temp_destination, destination)
