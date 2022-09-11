import os
import os.path
from django.db import models

from django_app.webserver.validators import check_file_extension, check_file_size

MEDIA_FOLDER_PATH = os.path.join(".", "django_app", "media")


def get_directory_for_file(user_id: str, csrf_token: str) -> str:
    return os.path.join("uploaded_files", f"user{user_id}", csrf_token[:10])


def get_destination_filepath(instance, filename: str) -> str:
    path = os.path.join(".", "uploaded_files", instance.processing_request.user_id, str(instance.processing_request.id),
                        filename)
    check_file_extension(instance, path)
    check_file_size(instance)

    # a file is present already
    filename_number = 1
    file_ending = get_file_extension(path)
    while os.path.isfile(os.path.join(MEDIA_FOLDER_PATH, path)):
        path_without_file_ending = path[:-len(file_ending)]

        # path is already numbered .path/filename_00.xxx
        if path_without_file_ending.split("_")[-1].isnumeric():
            number_string = path_without_file_ending.split("_")[-1]
            path_without_file_ending = path_without_file_ending[:-len(number_string) - 1]
        path = path_without_file_ending + f"_{filename_number}" + file_ending
        filename_number += 1

    return path


class ProcessingFilesRequest(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    user_id = models.CharField(max_length=64)
    csrf_token = models.CharField(max_length=32)
    date_of_request = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return "Object(ProcessingFilesRequest): " + str(self.pk)


class UploadedFile(models.Model):
    valid_file_endings = models.TextField(default="")
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    processing_request = models.ForeignKey(ProcessingFilesRequest, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    uploaded_file = models.FileField(upload_to=get_destination_filepath)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
