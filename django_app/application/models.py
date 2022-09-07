import os.path
import pathlib

from django.core.validators import FileExtensionValidator
from django.db import models


def get_directory_to_save_file_in(instance, filename: str) -> str:
    path = os.path.join("uploaded_files", f"user_{instance.user_id}", filename)
    extension_of_file = pathlib.Path(path).suffixes

    # check presence of the file and the extension
    if os.path.isfile(os.path.join(".", "media", path)) or extension_of_file[-1].lower() != '.pdf':
        path = os.path.join("invalid_files", f"user_{instance.user_id}", filename)

    return path


class UploadedFile(models.Model):
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    uploaded_file = models.ImageField(upload_to=get_directory_to_save_file_in)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
