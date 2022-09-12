import os
import shutil

from django_app.webserver.custom_models.path_parser import PathParser
from django_app.webserver.models import ProcessedFile, MEDIA_FOLDER_PATH, ProcessingFilesRequest
from pdfcompressor.utility.EventHandler import EventHandler
from pdfcompressor.utility.os_utility import OsUtility


class ProcessStatsEventHandler(EventHandler):
    def __init__(self, amount_of_input_files: int, result_files: list[ProcessedFile], request: ProcessingFilesRequest):
        super().__init__()
        self.__amount_of_input_files = amount_of_input_files
        self.__result_files = result_files
        self.__finished_files = 0
        self.__request = request
        self.__is_merger = len(result_files) > 1 and amount_of_input_files == 1

    def get_progress(self):
        return self.__finished_files / self.__amount_of_input_files

    def started_processing(self):
        self.__request.started = True
        self.__request.save()

    def postprocess(self, source_file: str, destination_file: str) -> None:
        self.__finished_files += 1
        if not self.__is_merger:
            for file in self.__result_files:
                if OsUtility.get_filename(destination_file) == OsUtility.get_filename(
                        str(file.processed_file_path)) + "_temp":
                    file.finished = True
                    file.save()

    def _zip_result_folder(self):
        result_file = self.__result_files[0]
        path_parser = PathParser(result_file.processed_file_path, self.__request.id, self.__request.path_extra)

        filename = path_parser.get_destination_filename(result_file.date_of_upload)
        compression_format = "zip"
        # create zip-archive
        shutil.make_archive(
            filename,
            compression_format,
            os.path.join(MEDIA_FOLDER_PATH, path_parser.get_source_dir())
        )

        zip_file = ProcessedFile.objects.get(
            processed_file_path=os.path.join(path_parser.get_source_dir(), filename + ".zip")
        )
        # move file into media folder
        shutil.move(
            os.path.join(".", filename + ".zip"),
            os.path.join(MEDIA_FOLDER_PATH, zip_file.processed_file_path)
        )
        for file in ProcessedFile.objects.filter(processing_request=self.__request):
            file.finished = True
            file.save()

    def finished_all_files(self):
        if self.__is_merger:
            self.__result_files[0].finished = True
            self.__result_files[0].save()
        self.__request.finished = True
        self.__request.save()
        self._zip_result_folder()
