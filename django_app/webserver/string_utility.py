# no django imports allowed inside this file, because it is used by task_scheduler.py
import os

MEDIA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "", "..", "media")


class StringUtility:
    @classmethod
    def get_merged_destination_filename(cls, path_extra: str, request_id: str, datetime):
        return f"{path_extra}_files_{request_id}_{cls.get_formatted_time(datetime)}"

    @classmethod
    def get_local_absolute_path(cls, download_path):
        return os.path.abspath(os.path.join(MEDIA_FOLDER_PATH, download_path))

    @classmethod
    def get_formatted_time(cls, t):
        return t.strftime("%d.%m.%Y-%H.%M.%S")

    @classmethod
    def get_filename_with_ending(cls, file_path: str) -> str:
        return file_path[len(os.path.dirname(file_path)) + 1:]
