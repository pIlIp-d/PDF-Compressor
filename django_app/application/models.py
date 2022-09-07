import os
import os.path
import pathlib

from django.core.exceptions import ValidationError
from django.db import models


def get_directory_to_save_file_in(instance, filename: str) -> str:
    path = os.path.join("uploaded_files", f"user_{instance.user_id}", filename)

    if len(path.split("_")) < 2:  # no number appended already
        path = path[:-4]  # todo APPEND NUMBER

    return path


def validate_file_size(file):
    filesize = file.size

    if filesize > UploadedFile.MAX_FILESIZE:
        raise ValidationError("The maximum file size that can be uploaded is unknown MB")
    elif file.name.lower().endswith(".pdf"):  # TODO dynamic file extensions
        raise ValidationError("File ending not accepted.")
    return file


class UploadedFile(models.Model):
    MAX_FILESIZE = 10000000
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    destination_path = get_directory_to_save_file_in
    uploaded_file = models.ImageField(upload_to=destination_path, verbose_name="", validators=[validate_file_size])
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
