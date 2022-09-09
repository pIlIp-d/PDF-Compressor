import os
import pathlib

from django.core.exceptions import ValidationError

MAX_FILESIZE = 100000000  # 100mb


def validate_file_extension(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1]  # returns path+filename
    valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        pass
    raise ValidationError("File extension isn't supported.")


def check_file_extension(path):
    extension_of_file = pathlib.Path(path).suffixes[-1].lower()
    if extension_of_file != '.pdf':
        raise ValidationError("Invalid extension. Only PDF-File's are allowed.")


def check_file_size(instance):
    file_size = instance.uploaded_file.size
    if file_size > MAX_FILESIZE:
        raise ValidationError("The maximum file size is reached.")
