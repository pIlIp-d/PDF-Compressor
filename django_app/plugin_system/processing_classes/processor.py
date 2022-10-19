import os
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from django_app.plugin_system.processing_classes.preprocessor import Preprocessor
from django_app.webserver.string_utility import StringUtility
from django_app.utility.event_handler import EventHandler
from django_app.utility.console_utility import ConsoleUtility
from django_app.utility.os_utility import OsUtility


# TODO eventHandler list isn't Threadsafe (when multiple processing requests are executed on the same Processor object)

class Processor(Postprocessor, Preprocessor, ABC):
    def __init__(
            self,
            event_handlers: list[EventHandler],
            file_type_from: str,
            file_type_to: str,
            can_merge: bool = False,
            run_multi_threaded: bool = True,
            processed_part: str = "All Files"
    ):
        if event_handlers is None:
            event_handlers = list()
        self._event_handlers = event_handlers
        self._preprocessors = []
        self._postprocessors = []
        self._add_event_handler_processors()
        self._processed_files_appendix = "_processed"
        self._processed_part = processed_part
        self._can_merge = can_merge
        self._file_type_from = file_type_from.lower()
        self._file_type_to = file_type_to.lower()
        self._run_multi_threaded = run_multi_threaded

    def _add_event_handler_processors(self) -> None:
        for event_handler in self._event_handlers:
            self.add_preprocessor(event_handler)
        for event_handler in self._event_handlers:
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
    def process_file(self, source_file: str, destination_path: str) -> None:
        pass

    def process_file_list(self, source_files: list, destination_files: list) -> None:
        for source_file, destination_file in zip(source_files, destination_files):
            self.process_file(source_file, destination_file)

    def process_file_list_multi_threaded(
            self,
            source_files: list,
            destination_files: list,
            cpu_count: int = os.cpu_count()
    ) -> None:
        args_list = [{"source_file": source, "destination_path": destination}
                     for source, destination in zip(source_files, destination_files)]
        self._custom_map_execute(self.process_file, args_list, cpu_count)

    def _get_temp_folder(self):
        while True:
            counter = uuid.uuid4()
            temp_file = os.path.abspath(
                os.path.join("", "temporary_files", str(counter) + self._processed_files_appendix))
            if not os.path.isdir(temp_file):
                return temp_file

    def _get_temp_destination(self, temp_folder, file_path: str):
        if self._string_is_file(file_path):
            return os.path.abspath(
                os.path.join(temp_folder, OsUtility.get_filename(file_path) + "." + self._file_type_to)
            )
        else:
            return os.path.abspath(
                os.path.join(temp_folder, os.path.basename(file_path))
            )

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        """
        Method needs to be implemented if 'can_merge' is set to True.
        It is called in self.process() if there are more than one source_file and just one destination_file
        :param file_list: files that are merged and removed afterwards
        :param merged_result_file: result file containing a merged version of the file_list
        """
        raise ValueError("If 'can_merge' is set to True the class must provide a _merge_files implementation.")

    def _string_is_file(self, path):
        return path.endswith(self._file_type_to)

    def _get_files_and_extra_info_from_input_folder(self, source_path, destination_path
                                                    ) -> tuple[list[str], list[str], bool, bool]:
        sources = OsUtility.get_file_list(source_path, self._file_type_from)
        merging = len(sources) > 1 and self._string_is_file(destination_path)
        output_folder = source_path + self._processed_files_appendix if destination_path == "default" else destination_path
        destinations = [
            os.path.join(
                output_folder,
                OsUtility.get_filename(file) + "." + self._file_type_to
            )
            for file in sources
        ]
        return sources, destinations, merging, False

    def _get_files_and_extra_info_from_input_file(self, source_path, destination_path
                                                  ) -> tuple[list[str], list[str], bool, bool]:
        input_path_without_file_ending = OsUtility.get_path_without_file_ending(source_path)

        if destination_path == "default":
            output_path = input_path_without_file_ending + self._processed_files_appendix + "." + self._file_type_to
        elif not self._string_is_file(destination_path):
            output_path = os.path.join(destination_path,
                                       os.path.basename(input_path_without_file_ending) + "." + self._file_type_to)
        else:
            output_path = destination_path
        return [source_path], [output_path], False, False

    def _get_files_and_extra_info(self, source_path, destination_path) -> tuple[list[str], list[str], bool, bool]:
        """
        :param source_path:
        :param destination_path:
        :return: source_file_list, destination_file_list, merged (length of lists must be equal)
        default behaviour (can optionally be changed via overwriting <br>
        _get_files_and_extra_info_from_input_folder, _get_files_and_extra_info_from_input_file in subclasses)<br><br>

        folder -> file: merges to file<br>
        folder -> folder: same filenames but in destination folder<br>
        file -> file: destination_file is the resulting file<br>
        file -> folder: a file with the same filename is created in destination folder<br>
        folder -> merge: same as folder -> folder but afterwards it merges into a default file in the directory of the
                                                                                source folder merge_#timestring#.xxx<br>
        file -> merge: merges into default a file in the directory of the source file merge_#timestring#.xxx<br>
        folder -> default: same as file -> folder, folder name <br>
        file -> default: merges into default a file in the directory of the source file merge_#timestring#.xxx<br>
        """
        return self._get_files_and_extra_info_from_input_folder(source_path, destination_path) if os.path.isdir(
            source_path) else self._get_files_and_extra_info_from_input_file(source_path, destination_path)

    def process(self, source_path, destination_path):
        if not os.path.exists(source_path):
            raise ValueError("No File or Folder was found at the given source_path.")

        force_merge = destination_path == "merge"
        if destination_path == "merge":
            source_dir = source_path if os.path.isdir(source_path) else os.path.dirname(source_path)
            destination_path = os.path.join(
                source_dir, "merged_" + StringUtility.get_formatted_time(datetime.now()) + "." + self._file_type_to
            )

        source_file_list, destination_path_list, is_merging, is_splitting = self._get_files_and_extra_info(
            source_path,
            destination_path
        )

        is_merging = force_merge or is_merging

        print(source_file_list, destination_path_list, is_merging, is_splitting)
        if len(source_file_list) == 0:
            raise ValueError("No files to Processed were found in the source_path.")

        # save size for comparison at the end
        orig_sizes = OsUtility.get_filesize_list(source_file_list)

        # create temporary destinations to avoid data loss
        temp_folder = self._get_temp_folder()
        temporary_destination_file_list = [
            self._get_temp_destination(temp_folder, path)
            for path in destination_path_list
        ]

        final_merge_file = None
        if is_merging:
            if not self._can_merge:
                raise ValueError("Merging is not supported for this Processor. " + str(self))
            final_merge_file = OsUtility.get_path_without_file_ending(
                temporary_destination_file_list[0]) + "_merged." + self._file_type_to

        for event_handler in self._event_handlers:
            event_handler.started_processing()

        # run processing
        if self._run_multi_threaded:
            self.process_file_list_multi_threaded(source_file_list, temporary_destination_file_list)
        else:
            self.process_file_list(source_file_list, temporary_destination_file_list)

        if is_merging:
            # move merge result to destination
            self._merge_files(temporary_destination_file_list, final_merge_file)
            ConsoleUtility.print_green(
                f"Merged {self._processed_part} into {ConsoleUtility.get_file_string(final_merge_file)}"
            )

        if is_merging:
            end_size = OsUtility.get_file_size(final_merge_file)
        else:
            end_size = sum(OsUtility.get_filesize_list(temporary_destination_file_list))
        # TODO move all (non-error) prints out of this class
        if len(source_file_list) > 1:
            ConsoleUtility.print_stats(sum(orig_sizes), end_size, self._processed_part)
            ConsoleUtility.print("\n")

        if is_merging and not is_splitting:
            OsUtility.move_file(final_merge_file, destination_path)
        elif is_splitting:
            for file in OsUtility.get_file_list(temporary_destination_file_list[0]):
                OsUtility.move_file(file, os.path.join(destination_path_list[0], os.path.basename(file)))
        else:
            for temp_destination, destination in zip(temporary_destination_file_list, destination_path_list):
                if os.path.isfile(temp_destination):
                    OsUtility.move_file(temp_destination, destination)

        # OsUtility.clean_up_folder(temp_folder)

        for event_handler in self._event_handlers:
            event_handler.finished_all_files()
