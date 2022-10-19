import os
import shutil

from django_app.task_scheduler.tasks.task import Task
from django_app.utility.os_utility import OsUtility


class ZipTask(Task):
    def __init__(self, folder_path: str, zip_file_path: str):
        super().__init__()
        self.__zip_file_path = zip_file_path
        self.__folder_path = folder_path

    def run(self):
        filename_without_file_ending = OsUtility.get_filename(self.__zip_file_path)

        # create zip-archive
        compression_format = "zip"
        shutil.make_archive(
            filename_without_file_ending,
            format=compression_format,
            root_dir=self.__folder_path
        )
        # move file into final destination
        shutil.move(
            os.path.join(".", filename_without_file_ending + ".zip"),
            os.path.join(self.__zip_file_path)
        )
