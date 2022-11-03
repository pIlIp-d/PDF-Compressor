# no django imports allowed inside this file, because it is used by task_scheduler.py
import os

MEDIA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "", "..", "media")

TIME_FORMAT = "%d.%m.%Y-%H.%M.%S"


class StringUtility:
    @classmethod
    def get_merged_destination_filename(cls, request_id: str, datetime):
        return f"processed_files_{request_id}_{cls.get_formatted_time(datetime)}"

    @classmethod
    def get_local_absolute_path(cls, download_path):
        return os.path.abspath(os.path.join(MEDIA_FOLDER_PATH, download_path))

    @classmethod
    def get_media_normalized_path(cls, absolute_path: str):
        absolute_media_path = os.path.abspath(MEDIA_FOLDER_PATH)
        if not absolute_path.startswith(absolute_media_path):
            raise ValueError("File is not inside the Media folder")
        return absolute_path[len(absolute_media_path)+1:]

    @classmethod
    def get_formatted_time(cls, t):
        return t.strftime(TIME_FORMAT)

    @classmethod
    def get_filename_with_ending(cls, file_path: str) -> str:
        return file_path[len(os.path.dirname(file_path)) + 1:]
