import os
import shutil

from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder
from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from django_app.plugin_system.processing_classes.event_handler import EventHandler


class RenamePngTask(ProcessingTask):
    def run(self):
        Renamer(
            self._request_parameters.get("new_filename_prefix"),
            super()._get_event_handler(),
            "png",
            "png"
        ).process(self._source_path, self._destination_path)


class Renamer(ProcessorWithDestinationFolder):
    def __init__(self, new_filename_prefix: str, event_handlers: list[EventHandler], file_type_from: str,
                 file_type_to: str):
        super().__init__(event_handlers, file_type_from, file_type_to)
        self._new_filename_prefix = new_filename_prefix

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        destination_file = os.path.join(
            destination_path,
            self._new_filename_prefix + os.path.basename(source_file)
        )

        if os.path.isfile(source_file):
            shutil.copyfile(source_file, destination_file)

        self.postprocess(source_file, destination_file)
