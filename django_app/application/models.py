import os
import os.path
import pathlib

from django.db import models


def get_directory_to_save_file_in(instance, filename: str) -> str:
    path = os.path.join("uploaded_files", f"user_{instance.user_id}", filename)

    if not is_valid_file_size:
        pass

    extension_of_file = pathlib.Path(path).suffixes

    # check presence of the file and the extension
    if os.path.isfile(os.path.join(".", "media", path)) or extension_of_file[-1].lower() != '.pdf':
        path = os.path.join("invalid_files", f"user_{instance.user_id}", filename)

    return path


def is_valid_file_size(path_of_file):
    file_size = os.path.getsize(path_of_file)
    print('File Size:', file_size, 'bytes')
    return file_size < 655350


class UploadedFile(models.Model):
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    destination_path = get_directory_to_save_file_in
    uploaded_file = models.ImageField(upload_to=destination_path)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
