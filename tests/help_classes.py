import os
import shutil

from django_app.plugin_system.processing_classes.event_handler import EventHandler
from django_app.plugin_system.processing_classes.processor import Processor
from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder
from django_app.utility.os_utility import OsUtility


class SimpleExampleProcessor(Processor):
    def __init__(self, event_handler: [EventHandler]):
        super().__init__(event_handler, ["txt"], "txt")

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


class SimpleProcessorForFileTypes(Processor):
    def __init__(self, file_type_from: list[str], file_type_to: str):
        super().__init__([], file_type_from, file_type_to)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        if destination_path.endswith("pdf"):
            raise ValueError("can't convert to that file type")
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


class SimpleFakeMergeProcessor(Processor):
    # used for testing can_merge but doesn't implement the _merge_files method
    def __init__(self, can_merge: bool):
        super().__init__([], ["txt"], "txt", can_merge=can_merge)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


class SimpleMergeProcessor(SimpleFakeMergeProcessor):
    # used for testing can_merge and implements the _merge_files method
    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        with open(merged_result_file, "w") as result_file:
            for file in file_list:
                with open(file) as f:
                    result_file.write(f.read())


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
    def __init__(self, event_handlers: list[EventHandler]):
        super().__init__(event_handlers, ["txt"], "txt")

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        shutil.copy(source_file, destination_path)
        self.postprocess(source_file, destination_path)


class SimpleMultiThreadTestProcessor(Processor):
    def __init__(self, event_handlers: list, run_multi_threaded: bool):
        super().__init__(event_handlers, ["txt"], "txt", run_multi_threaded)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


def clean_up_after_class():
    temp_dir = os.path.join(".", "temporary_files")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
