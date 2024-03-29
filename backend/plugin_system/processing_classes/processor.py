import os
import pathlib
import re
import shutil
import sys
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from functools import reduce
from glob import glob

from ansi.colour import fg

from plugin_system.processing_classes.postprocessor import Postprocessor
from plugin_system.processing_classes.preprocessor import Preprocessor
from django_app.settings import TIME_FORMAT
from plugin_system.processing_classes.event_handler import EventHandler
from plugin_system.processing_classes.processing_exception import ProcessingException


# TODO TODO test if recursive folders are still working
# TODO multi-threaded load balancing of available threads
# TODO eventHandler list isn't Threadsafe (when multiple processing requests are executed on the same Processor object)


class Processor(Postprocessor, Preprocessor, ABC):
    def __init__(
            self,
            event_handlers: list[EventHandler],
            file_type_from: list[str],
            file_type_to: str,
            can_merge: bool = False,
            run_multi_threaded: bool = True,
    ):
        """
        abstract class that simplifies file processing by only implementing process_file in subclasses
        :param event_handlers: list of EventHandlers of which the events are called in every stage of Processing
        :param file_type_from: list of source_files type e.g. ["png", "jpg", "jpeg"]
        :param file_type_to: type of result/processed files
        :param can_merge: enables the _merge_files() method after processing all files<br>
                -> _merge_files() must be implemented in subclass
        :param run_multi_threaded: allow to call process_file() for multiple files at the same time (multi threaded)
        """
        if event_handlers is None:
            event_handlers = list()
        self._event_handlers = event_handlers
        self._preprocessors = []
        self._postprocessors = []
        self.__add_event_handler_processors()
        self._processed_files_appendix = "_processed"
        self._can_merge = can_merge

        def without_dot_at_the_beginning(string):
            return string if not string.endswith(".") else string[1:]

        self._file_type_from = [without_dot_at_the_beginning(t).lower() for t in file_type_from]
        if file_type_to == "":
            raise ValueError("file_type_to cant be empty!")
        self._file_type_to = without_dot_at_the_beginning(file_type_to).lower()
        self._run_multi_threaded = run_multi_threaded

    def __add_event_handler_processors(self) -> None:
        for event_handler in self._event_handlers:
            self.add_preprocessor(event_handler)
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
    def _custom_map_execute(cls, method, args_list: list) -> list:
        futures = []
        with ProcessPoolExecutor() as executor:
            for method_parameter in args_list:
                futures.append(executor.submit(method, **method_parameter))
        return futures

    @classmethod
    def _copy_file(cls, from_file: str, to_file: str):
        # skip copy if equals
        if from_file == to_file:
            return
        # create directory if not already exists
        output_dir = os.path.dirname(to_file)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        shutil.copy(from_file, to_file)

    @classmethod
    def _get_file_size(cls, file_path: str) -> int:
        return 0 if not os.path.isfile(file_path) else os.stat(file_path).st_size

    @classmethod
    def _get_filesize_list(cls, file_list: list) -> list:
        return [cls._get_file_size(file) for file in file_list]

    @abstractmethod
    def process_file(self, source_file: str, destination_path: str) -> None:
        """
        process a source_file end create file/files in destination_path
        :param source_file: path to a file that is processed
        :param destination_path: path to a file or directory depending on class you are extending
        """
        pass

    def _process_file_list(self, source_files: list, destination_files: list) -> None:
        """
        sequential processing of files in source_files to destination_files<br>
        length of source_files and destination_files needs to be equal
        """
        if len(source_files) != len(destination_files):
            raise ValueError("length of 'source_files' and 'destination_files' needs to be equal.")
        for source_file, destination_file in zip(source_files, destination_files):
            self.process_file(source_file, destination_file)

    def process_file_list_multi_threaded(
            self,
            source_files: list[str],
            destination_files: list[str]
    ) -> None:
        """
        parallel processing of files in source_files to destination_files<br>
        length of source_files and destination_files needs to be equal
        :param source_files: list of source files
        :param destination_files: list of destination files/directories depending on the implementation of superclass
        """
        args_list = [{"source_file": source, "destination_path": destination}
                     for source, destination in zip(source_files, destination_files)]
        futures = self._custom_map_execute(self.process_file, args_list)
        # finally raise occurred exceptions
        for i, future in enumerate(futures):
            exception = future.exception()
            if exception is not None:
                raise ProcessingException(exception, args_list[i]["source_file"], args_list[i]["destination_path"])

    def _get_and_create_temp_folder(self) -> str:
        """
        creates and returns a unique folder path inside the project directory (used for internal file storing)
        """
        while True:
            counter = uuid.uuid4()
            temp_folder = os.path.abspath(
                os.path.join("", "temporary_files", str(counter) + self._processed_files_appendix)
            )
            if not os.path.isdir(temp_folder):
                return temp_folder

    def _get_temp_destination(self, temp_folder, destination_path: str):
        """
        merges temp_folder and destination_path to get a temporary destination path
        """
        if self._destination_path_string_is_file(destination_path):
            return os.path.abspath(
                os.path.join(temp_folder, self._get_filename(destination_path) + "." + self._file_type_to)
            )
        else:
            return os.path.abspath(
                os.path.join(temp_folder, os.path.basename(destination_path))
            )

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        """
        Method needs to be implemented if 'can_merge' is set to True.<br>
        It is called in self.process() if there are more than one source_file and just one destination_file
        :param file_list: files that are merged and removed afterwards
        :param merged_result_file: result file containing a merged version of the file_list
        """
        raise ValueError("If 'can_merge' is set to True the class must provide a _merge_files implementation.")

    def _destination_path_string_is_file(self, path) -> bool:
        return not os.path.isdir(path) and path.lower().endswith(self._file_type_to.lower())

    def _get_sources_files_by_file_type_from(self, source_path) -> list[str]:
        return list(set(reduce(
            lambda a, file_ending: a + glob(
                os.path.join(source_path, file_ending if file_ending == "*" else ("*" + file_ending))),
            self._file_type_from, []
        )))

    @classmethod
    def _get_filename(cls, full_path_to_file: str) -> str:
        filename_with_ending = os.path.basename(full_path_to_file)
        return re.split(r"\.[^.]*$", filename_with_ending)[0]

    @classmethod
    def get_path_without_file_ending(cls, path):
        return os.path.join(os.path.dirname(path), cls._get_filename(path))

    def __get_files_and_extra_info_from_input_folder(self, source_path, destination_path
                                                     ) -> tuple[list[str], list[str], bool, bool]:
        sources = self._get_sources_files_by_file_type_from(source_path)
        result_is_file = self._destination_path_string_is_file(destination_path)
        output_folder = source_path + self._processed_files_appendix if destination_path == "default" else destination_path
        # if destination file is specified but the program can skip merging, because there only is one file
        if result_is_file and len(sources) == 1:
            destinations = [destination_path]
        else:
            destinations = [
                os.path.join(output_folder, self._get_filename(file) + "." + self._file_type_to)
                for file in sources
            ]
        # sources, destinations, is_merging, is_splitting
        return sources, destinations, result_is_file and len(sources) > 1, False

    def __get_files_and_extra_info_from_input_file(self, source_path, destination_path
                                                   ) -> tuple[list[str], list[str], bool, bool]:
        input_path_without_file_ending = self.get_path_without_file_ending(source_path)
        if not reduce(lambda result, ending: result or source_path.lower().endswith(ending), self._file_type_from,
                      False):
            return [], [], False, False
        if destination_path == "default":
            output_path = input_path_without_file_ending + self._processed_files_appendix + "." + self._file_type_to
        elif not self._destination_path_string_is_file(destination_path):  # TODO proper mime type check
            output_path = os.path.join(destination_path,
                                       os.path.basename(input_path_without_file_ending) + "." + self._file_type_to)
        else:
            output_path = destination_path
        # sources, destinations, is_merging, is_splitting
        return [source_path], [output_path], False, False

    def _get_merge_destination(self, source_path):
        def get_filename_ending():
            return "_merged_" + datetime.now().strftime(TIME_FORMAT) + "." + self._file_type_to

        if os.path.isdir(source_path):
            return os.path.join(source_path + "_processed", source_path.split(os.sep)[-1] + get_filename_ending())
        else:
            return ".".join(source_path.split(".")[:-1]) + get_filename_ending()

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
        return self.__get_files_and_extra_info_from_input_folder(source_path, destination_path) if os.path.isdir(
            source_path) else self.__get_files_and_extra_info_from_input_file(source_path, destination_path)

    @staticmethod
    def _numerate_doubles(path_list: list[str]):
        found_doubles: dict[str, list[int]] = {}
        for i, path in enumerate(path_list):
            occurrences = path_list.count(path)
            if occurrences > 1:
                if found_doubles.get(path) is None:
                    found_doubles[path] = []
                found_doubles[path].append(i)

        for path, double in found_doubles.items():
            counter = 0
            for double_i in double:
                path_list[double_i] = "".join(path.split(".")[:-1]) + "_" + str(counter) + path.split(".")[-1]
                counter += 1

    def process(self, source_path, destination_path="default"):
        """
        implements advanced checks, behaviour, optimization for process_file<br>
        supports different situations and improves compatibility
        :param source_path: either path to a file or a folder
        :param destination_path: path to a file, folder, "default" or "merge"
        specific behavior is defined by _get_files_and_extra_info() and can be changed by overwriting the method
        """

        def is_valid_path(path):
            try:
                pathlib.Path(path).resolve()
                return True
            except (OSError, RuntimeError):
                return False

        if not is_valid_path(source_path):
            raise ValueError("Source Path %s is invalid." % source_path)
        if not is_valid_path(destination_path):
            raise ValueError("Destination Path %s is invalid." % destination_path)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"No File or Folder was found at the given source_path. '{source_path}'")

        # get usable lists of source, destination files
        force_merge = destination_path == "merge"
        if force_merge:
            destination_path = self._get_merge_destination(source_path)

        source_file_list, destination_path_list, is_merging, is_splitting = self._get_files_and_extra_info(
            source_path,
            destination_path
        )
        is_merging = force_merge or is_merging

        self._numerate_doubles(destination_path_list)

        if is_merging and not self._can_merge:
            raise ValueError("Merging is not supported for this Processor. " + str(self))

        if len(source_file_list) == 0:
            raise FileNotFoundError("No files to Process were found in the source_path.")

        # save size for comparison at the end
        orig_sizes = self._get_filesize_list(source_file_list)

        # create temporary destinations to avoid data loss
        temp_folder = self._get_and_create_temp_folder()
        os.makedirs(temp_folder, exist_ok=True)
        temporary_destination_file_list = [
            self._get_temp_destination(temp_folder, path)
            for path in destination_path_list
        ]

        temporary_merge_file = None
        if is_merging:
            temporary_merge_file = self.get_path_without_file_ending(
                temporary_destination_file_list[0]) + "_merged." + self._file_type_to

        for event_handler in self._event_handlers:
            event_handler.started_processing()

        # create destination directory
        if not is_splitting and self._destination_path_string_is_file(temporary_destination_file_list[0]):
            os.makedirs(os.path.dirname(temporary_destination_file_list[0]), exist_ok=True)
        else:
            os.makedirs(temporary_destination_file_list[0], exist_ok=True)

        # run processing
        if self._run_multi_threaded:
            self.process_file_list_multi_threaded(source_file_list, temporary_destination_file_list)
        else:
            self._process_file_list(source_file_list, temporary_destination_file_list)

        if is_merging:
            if is_splitting:
                self._merge_files(sorted(glob(os.path.join(temporary_destination_file_list[0], "*"))),
                                  temporary_merge_file)
            else:
                self._merge_files(sorted(temporary_destination_file_list), temporary_merge_file)
            for event_handler in self._event_handlers:
                event_handler.finished_merge()

        if is_merging:
            end_size = self._get_file_size(temporary_merge_file)
        else:
            end_size = sum(self._get_filesize_list(temporary_destination_file_list))

        self.print_stats(sum(orig_sizes), end_size)

        def move_file(from_file, to_file):
            self._copy_file(from_file, to_file)
            os.remove(from_file)

        if is_merging:
            move_file(temporary_merge_file, destination_path)
        elif is_splitting:
            for file in glob(os.path.join(temporary_destination_file_list[0], "*")):
                move_file(file, os.path.join(destination_path_list[0], os.path.basename(file)))
        else:
            for temp_destination, destination in zip(temporary_destination_file_list, destination_path_list):
                if os.path.isfile(temp_destination):
                    move_file(temp_destination, destination)
                else:
                    print("PathError temp_destination: %s, destination: %s" % (temp_destination, destination), file=sys.stderr)
        if is_merging:
            print(fg.green(f"Merged All Files into {fg.yellow(destination_path)}"))

        shutil.rmtree(temp_folder)#, ignore_errors=True)

        for event_handler in self._event_handlers:
            event_handler.finished_all_files()

    @classmethod
    def print_stats(cls, orig: int, result: int) -> None:
        if orig < 0:
            raise ValueError("orig must be greater than or equal to 0")
        if result < 0:
            raise ValueError("result can't be less than 0")
        orig_size = str(round(orig / 1000000, 2))
        result_size = str(round(result / 1000000, 2))
        percentage = 0 if orig == 0 else str(-1 * round(100 - (result / orig * 100), 2))
        print(fg.green(f"Processed Files. Size: from {orig_size}mb to {result_size}mb ({percentage}%)\n"))
