import os
from abc import ABC, abstractmethod

from plugins.crunch_compressor.processor.processor import Processor
from plugins.crunch_compressor.utility.EventHandler import EventHandler
from plugins.crunch_compressor.utility.console_utility import ConsoleUtility
from plugins.crunch_compressor.utility.io_path_parser import IOPathParser
from plugins.crunch_compressor.utility.os_utility import OsUtility


class Compressor(Processor, ABC):

    def __init__(
            self,
            event_handlers: list[EventHandler],
            file_type_from: str,
            file_type_to: str,
            can_merge: bool = False,
            processed_part: str = "All Files"
    ):
        super().__init__(event_handlers)
        self._file_type_from = file_type_from
        self._file_type_to = file_type_to
        self._can_merge = can_merge
        self._processed_part = processed_part
        self._final_merge_file = None

    @abstractmethod
    def compress_file(self, source_file: str, destination_file: str) -> None:
        pass

    @abstractmethod
    def compress_file_list(self, source_files: list, destination_files: list) -> None:
        pass

    def compress_file_list_multi_threaded(self, source_files: list, destination_files: list, cpu_count: int) -> None:
        args_list = [{"source_file": source, "destination_file": destination}
                     for source, destination in zip(source_files, destination_files)]
        self._custom_map_execute(self.compress_file, args_list, cpu_count)

    def _get_temp_file(self, filename: str):
        return os.path.abspath(
            os.path.join("", "temporary_files", OsUtility.get_filename(filename) + "_temp." + self._file_type_to)
        )

    def compress(self, source_path, destination_path):
        self._final_merge_file = ""

        io_path_parser = IOPathParser(source_path, destination_path, self._file_type_from, self._file_type_to,
                                      "_compressed")
        source_file_list = io_path_parser.get_input_file_paths()
        destination_file_list = io_path_parser.get_output_file_paths()

        is_merging = io_path_parser.is_merging()

        # save size for comparison at the end
        orig_sizes = OsUtility.get_filesize_list(source_file_list)

        # create temporary destinations to avoid data loss
        temporary_destination_file_list = [self._get_temp_file(file) for file in destination_file_list]

        if is_merging:
            if not self._can_merge:
                raise ValueError("Merging is not supported for this Processor." + str(self))
            self._final_merge_file = destination_file_list[0][:-4] + "_merged." + self._file_type_to
            destination_file_list = [destination_file_list[0] for _ in range(len(source_file_list))]
            temporary_destination_file_list = [temporary_destination_file_list[0] for _ in range(len(source_file_list))]

        for event_handler in self.event_handlers:
            event_handler.started_processing()

        self.compress_file_list(source_file_list, temporary_destination_file_list)

        if is_merging:
            # move merge result to destination
            OsUtility.move_file(temporary_destination_file_list[0], self._final_merge_file)
            ConsoleUtility.print_green(
                f"Merged {self._processed_part} into {ConsoleUtility.get_file_string(self._final_merge_file)}"
            )

        if is_merging:
            end_size = OsUtility.get_file_size(temporary_destination_file_list[0])
        else:
            end_size = sum(OsUtility.get_filesize_list(temporary_destination_file_list))

        if len(source_file_list) > 1:
            ConsoleUtility.print_stats(sum(orig_sizes), end_size, self._processed_part)
            ConsoleUtility.print("\n")

        if is_merging:
            OsUtility.move_file(self._final_merge_file, destination_path)
        else:
            for temp_destination, destination in zip(temporary_destination_file_list, destination_file_list):
                OsUtility.move_file(temp_destination, destination)

        for event_handler in self.event_handlers:
            event_handler.finished_all_files()
