import mimetypes
import subprocess
import sys

from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from plugin_system.processing_classes.processor import Processor


class ImageConverter(Processor):
    def __init__(self, file_type_to: str):
        super().__init__([], ["*"], file_type_to, False, False)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        command = rf"convert '{source_file}' '{destination_path}'"
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as cpe:
            print(repr(cpe), file=sys.stderr)
            print("processing failed during converting stage. (IGNORE)\n", file=sys.stderr)
            pass
        except Exception as e:
            print(repr(e), file=sys.stderr)  # dont raise e
        self.postprocess(source_file, destination_path)


class ImageConverterTask(ProcessingTask):
    def run(self):
        ImageConverter(
            mimetypes.guess_extension(self._request_parameters.get("result_file_type"))[1:],
        ).process(self._source_path)
