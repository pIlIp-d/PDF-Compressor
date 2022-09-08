import os
import os.path
import pathlib
from django.db import models
from jsons import ValidationError


def check_file_extension(path):
    extension_of_file = pathlib.Path(path).suffixes[-1].lower()
    if extension_of_file != '.pdf':
        raise ValidationError("Invalid extension. Only PDF-File's are allowed.")


def check_file_size(instance):
    file_size = instance.uploaded_file.size
    if file_size > UploadedFile.MAX_FILESIZE:
        raise ValidationError("The maximum file size is reached.")


def get_destination_directory(instance, filename: str) -> str:
    path = os.path.join("uploaded_files", f"user{instance.user_id}", filename)
    check_file_extension(path)
    check_file_size(instance)

    # TODO compute extension length
    filename_number = 1
    while os.path.isfile(os.path.join(".", "media", path)):
        path = path[:-4] + "(" + str(filename_number) + ")" + path[-4:]
        filename_number += 1

    return path



class UploadedFile(models.Model):
    MAX_FILESIZE = 10000000  # Bytes
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    uploaded_file = models.ImageField(upload_to=get_destination_directory)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
