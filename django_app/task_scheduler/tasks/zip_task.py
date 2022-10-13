import os
import shutil

from django_app.task_scheduler.tasks.task import Task
from django_app.webserver.string_utility import StringUtility


class ZipTask(Task):
    def __init__(self, folder_path: str, zip_file_path: str):
        super().__init__()
        self.__zip_file_path = zip_file_path
        self.__folder_path = folder_path

    def run(self):
        filename_without_file_ending = StringUtility.get_filename_with_ending(self.__zip_file_path)[:-len(".zip")]

        # create zip-archive
        compression_format = "zip"
        shutil.make_archive(
            filename_without_file_ending,
            compression_format,
            self.__folder_path
        )

        # move file into final destination
        shutil.move(
            os.path.join(".", filename_without_file_ending + ".zip"),
            os.path.join(self.__zip_file_path)
        )
