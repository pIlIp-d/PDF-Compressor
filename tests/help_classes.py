import shutil

from django_app.plugin_system.processing_classes.event_handler import EventHandler
from django_app.plugin_system.processing_classes.processor import Processor
from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder


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
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


def clean_up_after_class():
    temp_dir = os.path.join(".", "temporary_files")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
