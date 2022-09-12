import os
import os.path

from django.db import models

from .validators import check_file_extension, check_file_size, get_file_extension

MEDIA_FOLDER_PATH = os.path.join(".", "django_app", "media")


def get_formatted_time(t):
    return t.strftime("%d.%m.%Y-%H:%M:%S")


def get_uploaded_file_path(instance, filename: str) -> str:
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
    path_extra = models.TextField(default="")

    def __str__(self):
        return "Object(ProcessingFilesRequest): " + str(self.pk)

    class Meta:
        verbose_name_plural = 'Processing Files Requests'


def get_request_id(user_id: str, queue_csrf_token: str) -> int:
    return get_or_create_new_request(user_id, queue_csrf_token).id or -1


def get_request_by_id(request_id: int) -> ProcessingFilesRequest:
    return ProcessingFilesRequest.objects.filter(
        id=request_id
    ).first()


def get_or_create_new_request(user_id: str, queue_csrf_token: str, path_extra: str = "") -> ProcessingFilesRequest:
    processing_request = ProcessingFilesRequest.objects.filter(
        user_id=user_id,
        csrf_token=queue_csrf_token
    ).first()
    if path_extra != "":
        processing_request.path_extra = path_extra
    if processing_request is None:
        processing_request = ProcessingFilesRequest(
            user_id=user_id,
            csrf_token=queue_csrf_token,
            path_extra=path_extra
        )
    processing_request.save()
    return processing_request


class ProcessedFile(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    processing_request = models.ForeignKey(ProcessingFilesRequest, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    processed_file_path = models.TextField()
    date_of_upload = models.DateTimeField(auto_now_add=True)
    merger = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ": " + str(self.processed_file_path)

    class Meta:
        verbose_name_plural = 'Processed files'

    @classmethod
    def add_processed_file_by_id(cls, processed_file_path: str, processing_request_id: int, ):
        return cls.add_processed_file(processed_file_path, get_request_by_id(processing_request_id))

    @classmethod
    def add_processed_file(cls, processed_file_path: str, processing_request: ProcessingFilesRequest):
        processed_file = ProcessedFile(
            processed_file_path=processed_file_path,
            processing_request=processing_request
        )
        processed_file.save()
        return processed_file


def get_all_processing_files(user_id: str):
    def simplify_filename(path: str) -> str:
        return path[len(os.path.dirname(path)) + 1:]

    all_user_requests = ProcessingFilesRequest.objects.filter(
        user_id=user_id
    )
    all_files = []
    for request in all_user_requests:
        request_files = []
        for file in UploadedFile.objects.filter(processing_request=request).order_by('date_of_upload'):
            request_files.append({
                "file_id": file.id,
                "filename": simplify_filename(file.uploaded_file.name) + " (Original)",
                "request_id": file.processing_request.id,
                "date_of_upload": get_formatted_time(file.date_of_upload)
            })
        for processed_file in ProcessedFile.objects.filter(processing_request=request).order_by('date_of_upload'):
            if processed_file.processing_request.id == request.id:
                request_files.append({
                    "file_id": processed_file.id,
                    "filename": simplify_filename(processed_file.processed_file_path),
                    "request_id": request.id,
                    "date_of_upload": get_formatted_time(processed_file.date_of_upload)
                })
        all_files.append(reversed(request_files))
    return reversed(all_files)


class UploadedFile(models.Model):
    valid_file_endings = models.TextField(default="")
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    processing_request = models.ForeignKey(ProcessingFilesRequest, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to=get_uploaded_file_path)
    date_of_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk) + ": " + str(self.uploaded_file.name)

    class Meta:
        verbose_name_plural = 'Uploaded files'


def get_file_list_of_current_request(request_id):
    return UploadedFile.objects.filter(
        processing_request=get_request_by_id(request_id)
    )
