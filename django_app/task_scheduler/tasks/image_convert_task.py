import os

from PIL import Image

from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from plugins.crunch_compressor.utility.os_utility import OsUtility


class ImageConvertClass(ProcessingTask):
    def run(self):
        event_handlers = super()._get_process_stats_event_handler()
        source_path = self._parameters.pop("source_path")
        destination_path = self._parameters.pop("destination_path")
        new_file_ending = self._parameters.pop("result_file_types")
        for event_handler in event_handlers:
            event_handler.started_processing()

        for img_path in OsUtility.get_file_list(source_path):
            image_destination = os.path.join(destination_path, img_path.split(".")[:-1] + new_file_ending)
            # pre-process
            for event_handler in event_handlers:
                event_handler.preprocess(img_path, image_destination)

            # open, convert and save image
            with Image.open(img_path) as img:
                img.convert(new_file_ending[1:])
                img.save(image_destination)

            # post-process
            for event_handler in event_handlers:
                event_handler.postprocess(img_path, image_destination)

        for event_handler in event_handlers:
            event_handler.finished_all_files()
