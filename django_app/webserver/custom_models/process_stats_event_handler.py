import os
import shutil
from time import sleep

import jsons
import requests

from django_app.webserver.custom_models.string_utility import StringUtility
from manage import ADDRESS, PORT, METHOD
from pdfcompressor.utility.EventHandler import EventHandler
from pdfcompressor.utility.os_utility import OsUtility


class ProcessStatsEventHandler(EventHandler):
    def __init__(self, amount_of_input_files: int, result_files: list, request_id: int):
        super().__init__()
        self.__amount_of_input_files = amount_of_input_files
        self.__result_files = result_files
        self.__request_id = request_id
        self.__finished_files = 0
        self.__is_merger = len(result_files) == 1 and amount_of_input_files > 1

    def get_progress(self):
        return self.__finished_files / self.__amount_of_input_files

    @staticmethod
    def __make_request(request_string: str, args):
        for i in range(3):  # retry 3 times on failure
            status = requests.get(f"{METHOD}://{ADDRESS}:{PORT}/api" + request_string, args)
            if status != 200:
                sleep(1)
            else:
                return jsons.loads(status.text)

    def started_processing(self):
        self.__make_request("/started_request_processing", {"request_id": str(self.__request_id)})

    def postprocess(self, source_file: str, destination_file: str) -> None:
        self.__finished_files += 1
        if not self.__is_merger:
            for file in self.__result_files[1:]:
                if OsUtility.get_filename(destination_file) == OsUtility.get_filename(
                        str(file.processed_file_path)) + "_temp":
                    self.__make_request("/finish_file", {"processed_file_path": file.processed_file_path})

    def _zip_result_folder(self):
        result_file = self.__result_files[0]
        destination_directory = os.path.dirname(result_file)
        filename_without_file_ending = StringUtility.get_filename_with_ending(result_file)[:-len(".zip")]

        # create zip-archive
        compression_format = "zip"
        shutil.make_archive(
            filename_without_file_ending,
            compression_format,
            StringUtility.get_local_relative_path(destination_directory)
        )

        # move file into media folder
        shutil.move(
            os.path.join(".", filename_without_file_ending + ".zip"),
            StringUtility.get_local_relative_path(os.path.join(destination_directory, filename_without_file_ending + ".zip"))
        )
        self.__make_request("/finish_request", {"request_id": str(self.__request_id)})

    def finished_all_files(self):
        if self.__is_merger:
            self.__make_request("/finish_file", {"processed_file_path": self.__result_files[1].processed_file_path})

        self._zip_result_folder()
