import os
import os.path
import pathlib
from django.db import models
from jsons import ValidationError

MEDIA_FOLDER_PATH = os.path.abspath(os.path.join(".", "media"))


def get_directory_for_file(user_id: str, csrf_token: str) -> str:
    return os.path.join("uploaded_files", f"user{user_id}", csrf_token[:10])


def check_file_extension(path):
    extension_of_file = pathlib.Path(path).suffixes[-1].lower()
    if extension_of_file != '.pdf':
        raise ValidationError("Invalid extension. Only PDF-File's are allowed.")


def check_file_size(instance):
    file_size = instance.uploaded_file.size
    if file_size > UploadedFile.MAX_FILESIZE:
        raise ValidationError("The maximum file size is reached.")


# todo use request_queue id for file path, because it is getting too long (id from csrf_token) new Model=processing_request
def get_destination_directory(instance, filename: str) -> str:
    path = os.path.join(get_directory_for_file(instance.user_id, instance.csrf_token), filename)
    check_file_extension(path)
    check_file_size(instance)

    # TODO compute extension length
    filename_number = 1
    while os.path.isfile(os.path.join(MEDIA_FOLDER_PATH, path)):
        path = path[:-4] + "(" + str(filename_number) + ")" + path[-4:]
        filename_number += 1

    return path


class UploadedFile(models.Model):
    MAX_FILESIZE = 100000000  # 100mb
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    uploaded_file = models.FileField(upload_to=get_destination_directory)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
