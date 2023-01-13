import os
import shutil
import sys
import time
from io import StringIO

from django_app.plugin_system.processing_classes.event_handler import EventHandler
from django_app.plugin_system.processing_classes.processor import Processor
from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder

TESTDATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "TestData"))
TESTDATA_DIR_WITHOUT_RELATIVE = "/".join(TESTDATA_DIR.split(os.path.sep))


def get_console_buffer(std_type: str) -> StringIO:
    console_buffer = StringIO()
    if std_type == "stdout":
        sys.stdout = console_buffer
    elif std_type == "stderr":
        sys.stderr = console_buffer
    else:
        raise ValueError("unsupported std_type")
    return console_buffer


def simple_copy_process_file(self, source_file: str, destination_path: str) -> None:
    self.preprocess(source_file, destination_path)
    shutil.copyfile(source_file, destination_path)
    self.postprocess(source_file, destination_path)


def simple_merge_files(self, file_list: list[str], merged_result_file: str) -> None:
    with open(merged_result_file, "w") as result_file:
        for file in file_list:
            with open(file) as f:
                result_file.write(f.read())


class SimpleExampleProcessor(Processor):
    def __init__(self, event_handlers=None, **kwargs):
        if event_handlers is None:
            event_handler = []
        super().__init__(event_handlers, ["txt"], "txt", **kwargs)

    def process_file(self, source_file: str, destination_path: str) -> None:
        simple_copy_process_file(self, source_file, destination_path)

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        simple_merge_files(self, file_list, merged_result_file)


class SimpleProcessorForFileTypes(Processor):
    def __init__(self, file_type_from: list[str], file_type_to: str):
        super().__init__([], file_type_from, file_type_to)

    def process_file(self, source_file: str, destination_path: str) -> None:
        if destination_path.endswith("pdf"):
            raise ValueError("can't convert to that file type")
        simple_copy_process_file(self, source_file, destination_path)


class SimpleFakeMergeProcessor(Processor):
    # used for testing can_merge but doesn't implement the _merge_files method
    def __init__(self, can_merge: bool):
        super().__init__([], ["txt"], "txt", can_merge=can_merge)

    def process_file(self, source_file: str, destination_path: str) -> None:
        simple_copy_process_file(self, source_file, destination_path)


class SimpleMergeProcessor(SimpleFakeMergeProcessor):
    # used for testing can_merge and implements the _merge_files method
    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        simple_merge_files(self, file_list, merged_result_file)


class FailedProcessingException(Exception):
    pass


class ErrorProcessor(Processor):
    def __init__(self, event_handlers: list[EventHandler]):
        super().__init__(event_handlers, ["txt"], "txt")

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        raise FailedProcessingException
        self.postprocess(source_file, destination_path)


class DestinationFolderSubClass(ProcessorWithDestinationFolder):
    def __init__(self, event_handlers=None, **kwargs):
        if event_handlers is None:
            event_handlers = []
        super().__init__(event_handlers, ["txt"], "txt", **kwargs)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        with open(source_file) as file:
            file_content = file.read()
            for line_num, line in enumerate(file_content.split("\n")):
                result_file = os.path.join(destination_path,
                                           os.path.basename(source_file)[:-4] + "_line_%s.txt" % line_num)
                with open(result_file, "w") as new_file:
                    new_file.write(line)
        self.postprocess(source_file, destination_path)

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        simple_merge_files(self, file_list, merged_result_file)


class SimpleMultiThreadTestProcessor(Processor):
    def __init__(self, event_handlers: list, run_multi_threaded: bool):
        super().__init__(event_handlers, ["txt"], "txt", run_multi_threaded=run_multi_threaded)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        time.sleep(0.001)
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


def clean_up_after_class():
    temp_dir = os.path.join(".", "temporary_files")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
