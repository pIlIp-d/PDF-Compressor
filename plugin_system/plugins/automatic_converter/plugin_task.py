from ffmpeg import FFmpeg

from wand.image import Image

from plugin_system.processing_classes.processor import Processor
from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from plugin_system.processing_classes.event_handler import EventHandler


class AutomaticConvertTask(ProcessingTask):
    def run(self):
        AutomaticConvert(
            super()._get_event_handler(),
            "", "".join(self._request_parameters.get("new_filetype").split(".")[1:])
        ).process(self._source_path, self._destination_path)


class AutomaticConvert(Processor):
    def __init__(self, event_handlers: list[EventHandler], file_type_from: str, file_type_to: str):
        super().__init__(event_handlers, [file_type_from], file_type_to)

    def __automatic_image_convert(self, source_file: str, destination_path: str):
        ny = Image(filename=source_file)
        ny_convert = ny.convert(self._file_type_to.split(".")[-1])
        ny_convert.save(filename=destination_path)

    def __automatic_video_audio_convert(self, source_file: str, destination_path: str):
        ffmpeg = (FFmpeg().option("y").input(source_file).output(destination_path))
        ffmpeg.execute()

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        print(destination_path)
        try:
            self.__automatic_image_convert(source_file, destination_path)
        except Exception as e1:
            try:
                self.__automatic_video_audio_convert(source_file, destination_path)
            except Exception as e2:
                raise Exception("automatic convert Failed.")

        self.postprocess(source_file, destination_path)
