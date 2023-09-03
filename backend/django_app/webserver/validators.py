import pathlib

from django.core.exceptions import ValidationError

MAX_FILESIZE = 100000000  # 100mb


def get_file_extension(path: str) -> str:
    return pathlib.Path(path).suffixes[-1].lower()


def check_file_extension(instance, path): # TODO
    extension_of_file = get_file_extension(path)
    if extension_of_file not in str(instance.valid_file_endings).split(","):
        raise ValidationError("Invalid File extension.")


def check_file_size(instance):
    file_size = instance.uploaded_file.size
    if file_size > MAX_FILESIZE:
        raise ValidationError("The maximum file size is reached.")
