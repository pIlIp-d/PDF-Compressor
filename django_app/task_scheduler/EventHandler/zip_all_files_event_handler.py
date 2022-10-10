import os
import shutil
from django_app.webserver.custom_models.string_utility import StringUtility
from plugins.crunch_compressor.utility.EventHandler import EventHandler


class ZipAllFilesEventHandler(EventHandler):
    def __init__(self, zip_file_path: str):
        super().__init__()
        self.__zip_file_path = zip_file_path

    def finished_all_files(self):
        destination_directory = os.path.dirname(self.__zip_file_path)
        filename_without_file_ending = StringUtility.get_filename_with_ending(self.__zip_file_path)[:-len(".zip")]

        # create zip-archive
        compression_format = "zip"
        shutil.make_archive(
            filename_without_file_ending,
            compression_format,
            StringUtility.get_local_absolute_path(destination_directory)
        )

        # move file into media folder
        shutil.move(
            os.path.join("../../webserver/custom_models", filename_without_file_ending + ".zip"),
            StringUtility.get_local_absolute_path(
                os.path.join(destination_directory, filename_without_file_ending + ".zip"))
        )
