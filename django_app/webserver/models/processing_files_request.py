import os
from time import strftime

from django.core.files.uploadedfile import UploadedFile
from django.db import models

from django_app.webserver.models.processed_file import ProcessedFile
from django_app.webserver.string_utility import StringUtility


class ProcessingFilesRequest(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    user_id = models.CharField(max_length=64)
    request_id = models.CharField(max_length=64)
    date_of_request = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    path_extra = models.TextField(default="")

    def __str__(self):
        return "Object(ProcessingFilesRequest): " + str(self.pk)

    class Meta:
        verbose_name_plural = 'Processing Files Requests'

    def file_count(self):
        return len(UploadedFile.objects.filter(processing_request=self)) \
               + len(ProcessedFile.objects.filter(processing_request=self))

    def get_source_dir(self):
        return os.path.join("uploaded_files", str(self.user_id), str(self.id))

    def get_destination_dir(self):
        return self.get_source_dir() + "_" + str(self.path_extra)

    def get_merged_destination_filename(self, datetime):
        return StringUtility.get_merged_destination_filename(str(self.path_extra), str(self.id), datetime)

    def get_merged_destination_path(self, datetime: strftime, file_ending_including_dot: str):
        return os.path.join(
            self.get_destination_dir(),
            self.get_merged_destination_filename(datetime) + file_ending_including_dot
        )

    def get_zip_destination_path(self, datetime: strftime):
        return self.get_merged_destination_path(datetime, ".zip")

    def get_destination_path(self, source_file):
        return os.path.join(
            self.get_destination_dir(),
            source_file[len(self.get_source_dir()) + 1:]  # get only the filename
        )

    @classmethod
    def get_uploaded_file_list_of_current_request(cls, request):
        return UploadedFile.objects.filter(
            processing_request=request
        )

    @classmethod
    def get_request_by_id(cls, processing_files_request_id: int):
        return cls.objects.filter(
            id=processing_files_request_id
        ).first()

    @classmethod
    def get_or_create_new_request(cls, user_id: str, request_id: str):
        return cls.objects.get_or_create(
            user_id=user_id,
            request_id=request_id
        )[0]
