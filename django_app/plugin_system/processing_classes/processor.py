import os
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
import inspect
from functools import wraps

from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from django_app.plugin_system.processing_classes.preprocessor import Preprocessor
from plugins.crunch_compressor.utility.EventHandler import EventHandler
from plugins.crunch_compressor.utility.console_utility import ConsoleUtility
from plugins.crunch_compressor.utility.io_path_parser import IOPathParser
from plugins.crunch_compressor.utility.os_utility import OsUtility


class Processor(Postprocessor, Preprocessor, ABC):
    def __init__(
            self,
            event_handlers: list[EventHandler],
            file_type_from: str,
            file_type_to: str,
            processed_files_appendix: str = "_processed",
            can_merge: bool = False,
            processed_part: str = "All Files"
    ):
        self.event_handlers = event_handlers
        self._preprocessors = []
        self._postprocessors = []
        self._add_event_handler_processors()
        self._processed_files_appendix = processed_files_appendix
        self._processed_part = processed_part
        self._can_merge = can_merge
        self._file_type_from = file_type_from
        self._file_type_to = file_type_to
        self._final_merge_file = None

    def _add_event_handler_processors(self) -> None:
        for event_handler in self.event_handlers:
            self.add_preprocessor(event_handler)
        for event_handler in self.event_handlers:
            self.add_postprocessor(event_handler)

    def add_preprocessor(self, processor: Preprocessor) -> None:
        self._preprocessors.append(processor)

    def add_postprocessor(self, processor: Postprocessor) -> None:
        self._postprocessors.append(processor)

    def preprocess(self, source_file: str, destination_file: str) -> None:
        for processor in self._preprocessors:
            processor.preprocess(source_file, destination_file)

    def postprocess(self, source_file: str, destination_file: str) -> None:
        for processor in self._postprocessors:
            processor.postprocess(source_file, destination_file)

    @classmethod
    def _custom_map_execute(cls, method, args_list: list, cpu_count: int) -> None:
        with ProcessPoolExecutor(max_workers=cpu_count) as executor:
            for method_parameter in args_list:
                executor.submit(method, **method_parameter)

    @abstractmethod
    def process_file(self, source_file: str, destination_file: str) -> None:
        pass

    @abstractmethod
    def process_file_list(self, source_files: list, destination_files: list) -> None:
        pass

    def process_file_list_multi_threaded(self, source_files: list, destination_files: list, cpu_count: int) -> None:
        args_list = [{"source_file": source, "destination_file": destination}
                     for source, destination in zip(source_files, destination_files)]
        self._custom_map_execute(self.process_file, args_list, cpu_count)

    def _get_temp_file(self, filename: str):
        return os.path.abspath(
            os.path.join("", "temporary_files", OsUtility.get_filename(filename) + "_temp." + self._file_type_to)
        )

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        """
        Method needs to be implemented if 'can_merge' is set to True.
        It is called in self.process() if there are more than one source_file and just one destination_file
        :param file_list: files that are merged and removed afterwards
        :param merged_result_file: result file containing a merged version of the file_list
        """
        raise NotImplementedError("If 'can_merge' is set to True the class must provide a _merge_files implementation.")

    def process(self, source_path, destination_path):
        # reset after each run
        self._final_merge_file = None

        io_path_parser = IOPathParser(
            source_path,
            destination_path,
            self._file_type_from,
            self._file_type_to,
            self._processed_files_appendix
        )
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

            self._final_merge_file = OsUtility.get_path_without_file_ending(
                temporary_destination_file_list[0]) + "_merged." + self._file_type_to

        for event_handler in self.event_handlers:
            event_handler.started_processing()

        self.process_file_list(source_file_list, temporary_destination_file_list)

        if is_merging:
            # move merge result to destination
            self._merge_files(temporary_destination_file_list, self._final_merge_file)
            ConsoleUtility.print_green(
                f"Merged {self._processed_part} into {ConsoleUtility.get_file_string(self._final_merge_file)}"
            )

        if is_merging:
            end_size = OsUtility.get_file_size(self._final_merge_file)
        else:
            end_size = sum(OsUtility.get_filesize_list(temporary_destination_file_list))
        # TODO move all (non-error) prints out of this class
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
