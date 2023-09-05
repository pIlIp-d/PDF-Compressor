import mimetypes
import subprocess
import sys

from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from plugin_system.processing_classes.event_handler import EventHandler
from plugin_system.processing_classes.processor import Processor


class FfmpegConverter(Processor):
    def __init__(self, file_type_to: str, event_handlers: list[EventHandler]):
        super().__init__(event_handlers, ["*"], file_type_to, False, False)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        command = rf"ffmpeg -i '{source_file}' '{destination_path}'"
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as cpe:
            print(repr(cpe), file=sys.stderr)
            print("processing failed during converting stage. (IGNORE)\n", file=sys.stderr)
            pass
        except Exception as e:
            print(repr(e), file=sys.stderr)  # dont raise e
        self.postprocess(source_file, destination_path)


class FfmpegConverterTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        FfmpegConverter(
            mimetypes.guess_extension(self._request_parameters.get("result_file_type"))[1:],
            event_handlers=event_handler
        ).process(self._source_path)
