import os

from django_app.webserver.models import get_formatted_time


class PathParser:  # TODO testing
    def __init__(self, initial_path: str, request_id: int, path_extra: str):
        self.__initial_path = initial_path
        self.__request_id = request_id
        self.__path_extra = path_extra

    @classmethod
    def get_file_ending(cls, file_path):
        return file_path.split(".")[-1]

    def get_default_file_ending(self):
        return self.get_file_ending(self.__initial_path)

    def get_compressed_dir(self) -> str:
        return self.get_source_dir() + "_" + self.__path_extra

    def get_source_dir(self) -> str:
        return os.path.dirname(self.__initial_path)

    def get_destination_filename(self, datetime):
        return f"{self.__path_extra}_files_{str(self.__request_id)}_{get_formatted_time(datetime)}"

    def get_merged_destination_path(self, datetime):
        return os.path.join(self.get_compressed_dir(),
                            self.get_destination_filename(datetime) + self.get_default_file_ending())

    def get_zip_destination_path(self, datetime):
        return os.path.join(self.get_compressed_dir(), self.get_destination_filename(datetime) + ".zip")

    def get_destination_path(self, source_file):
        return os.path.join(
            self.get_compressed_dir(),
            source_file[len(self.get_source_dir()) + 1:]
        )
