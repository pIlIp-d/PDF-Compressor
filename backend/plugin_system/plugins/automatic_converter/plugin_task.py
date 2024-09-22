from celery import shared_task
from ffmpeg import FFmpeg

from wand.image import Image


class AutomaticConvert:
    def __init__(self, file_type_from: str, file_type_to: str):
        super().__init__([], [file_type_from], file_type_to)

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
        except Exception:
            try:
                self.__automatic_video_audio_convert(source_file, destination_path)
            except Exception:
                raise Exception("automatic convert Failed.")

        self.postprocess(source_file, destination_path)


@shared_task
def automaticConvertTask(request_parameters, source_path, destination_path):
    AutomaticConvert(
        file_type_from="",
        file_type_to="".join(request_parameters.get("new_filetype").split(".")[1:]
                             )
    ).process(source_path, destination_path)
