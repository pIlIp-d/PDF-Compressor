import os

from django.db import models

from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.string_utility import StringUtility
from django_app.webserver.validators import check_file_extension, check_file_size, get_file_extension


def get_uploaded_file_path(instance, filename: str) -> str:
    filename = filename.replace(" ", "_")
    path = os.path.join(
        ".", "uploaded_files",
        instance.processing_request.user_id,
        str(instance.processing_request.id),
        filename
    )
    check_file_extension(instance, path)
    check_file_size(instance)

    # a file is present already
    filename_number = 1
    file_ending = get_file_extension(path)
    while os.path.isfile(StringUtility.get_local_absolute_path(path)):
        path_without_file_ending = path[:-len(file_ending)]

        # path is already numbered .path/filename_00.xxx
        if path_without_file_ending.split("_")[-1].isnumeric():
            number_string = path_without_file_ending.split("_")[-1]
            path_without_file_ending = path_without_file_ending[:-len(number_string) - 1]

        # create file path with increased number
        path = path_without_file_ending + f"_{filename_number}" + file_ending
        filename_number += 1

    return path


class UploadedFile(models.Model):
    valid_file_endings = models.TextField(default="")
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    processing_request = models.ForeignKey(ProcessingFilesRequest, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to=get_uploaded_file_path, max_length=255)
    date_of_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk) + ": " + str(self.uploaded_file.name)

    def delete(self, using=None, keep_parents=False):
        self.uploaded_file.delete()
        super(UploadedFile, self).delete(using, keep_parents)

    @classmethod
    def get_uploaded_file_list_of_current_request(cls, request):
        return cls.objects.filter(
            processing_request=request
        )

    class Meta:
        verbose_name_plural = 'Uploaded files'
