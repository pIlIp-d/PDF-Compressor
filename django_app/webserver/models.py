import os
import os.path
from time import strftime

from django.db import models

from .custom_models.string_utility import StringUtility
from .validators import check_file_extension, check_file_size, get_file_extension


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
    while os.path.isfile(StringUtility.get_local_relative_path(path)):
        path_without_file_ending = path[:-len(file_ending)]

        # path is already numbered .path/filename_00.xxx
        if path_without_file_ending.split("_")[-1].isnumeric():
            number_string = path_without_file_ending.split("_")[-1]
            path_without_file_ending = path_without_file_ending[:-len(number_string) - 1]

        # create file path with increased number
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
            self.get_destination_dir(), self.get_merged_destination_filename(datetime) + file_ending_including_dot)

    def get_zip_destination_path(self, datetime: strftime):
        return self.get_merged_destination_path(datetime, ".zip")

    def get_destination_path(self, source_file):
        return os.path.join(
            self.get_destination_dir(),
            source_file[len(self.get_source_dir()) + 1:]  # get only the filename
        )

    @classmethod
    def __get_request(cls, user_id: str, queue_csrf_token: str):
        return cls.objects.filter(
            user_id=user_id,
            csrf_token=queue_csrf_token
        ).first()

    @classmethod
    def get_uploaded_file_list_of_current_request(cls, request_id: int):
        return UploadedFile.objects.filter(
            processing_request=cls.get_request_by_id(request_id)
        )

    @classmethod
    def get_processed_file_list_of_current_request(cls, request_id: int):
        return ProcessedFile.objects.filter(
            processing_request=cls.get_request_by_id(request_id)
        )

    @classmethod
    def get_request_id(cls, user_id: str, queue_csrf_token: str) -> int:
        return cls.get_or_create_new_request(user_id, queue_csrf_token).id or -1

    @classmethod
    def get_request_by_id(cls, request_id: int):
        return cls.objects.filter(
            id=request_id
        ).first()

    @classmethod
    def get_or_create_new_request(cls, user_id: str, queue_csrf_token: str, path_extra: str = ""):
        processing_request = cls.objects.get_or_create(
            user_id=user_id,
            csrf_token=queue_csrf_token,
            defaults={"path_extra": path_extra}
        )[0]
        # TODO small files will add two requests, because they are uploaded too fast.
        #  Create request on main_view display
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

    def delete(self, using=None, keep_parents=False):
        file = StringUtility.get_local_relative_path(self.processed_file_path)
        if os.path.isfile(file):
            os.remove(file)
        if self.processing_request.file_count() <= 1:
            self.processing_request.delete()
        super(ProcessedFile, self).delete(using, keep_parents)

    class Meta:
        verbose_name_plural = 'Processed files'

    @classmethod
    def add_processed_file_by_id(cls, processed_file_path: str, processing_request_id: int):
        return cls.add_processed_file(
            processed_file_path,
            ProcessingFilesRequest.get_request_by_id(processing_request_id)
        )

    @classmethod
    def add_processed_file(cls, processed_file_path: str, processing_request: ProcessingFilesRequest):
        processed_file = cls(
            processed_file_path=processed_file_path,
            processing_request=processing_request
        )
        processed_file.save()
        return processed_file

    @classmethod
    def get_all_processing_files(cls, user_id: str):

        def ___get_json(file_obj, filename: str, filename_path: str, finished: bool, request_id: int, file_origin: str):
            return {
                "file_id": file_obj.id,
                "filename": StringUtility.get_filename_with_ending(filename),
                "filename_path": os.path.join("media", filename_path),
                "finished": finished,
                "request_id": request_id,
                "date_of_upload": StringUtility.get_formatted_time(file_obj.date_of_upload),
                "file_origin": file_origin,
                "size": "%.2fmb" % (
                    0 if not finished or not os.path.isfile(StringUtility.get_local_relative_path(filename_path))
                    else os.path.getsize(StringUtility.get_local_relative_path(filename_path)) / 1000000)
            }

        def ___get_source_files(processing_request):
            files = []
            for file in UploadedFile.objects.filter(processing_request=processing_request).order_by('date_of_upload'):
                files.append(___get_json(
                    file_obj=file, filename=file.uploaded_file.name + " (Original)",
                    filename_path=file.uploaded_file.name, finished=True, request_id=processing_request.id,
                    file_origin="uploaded"
                ))
            return files

        def ___get_processed_files(processing_request):
            files = []
            for processed_file in ProcessedFile.objects.filter(processing_request=processing_request).order_by(
                    'date_of_upload'):
                if processed_file.processing_request.id == processing_request.id:
                    files.append(___get_json(
                        file_obj=processed_file, filename=processed_file.processed_file_path,
                        filename_path=processed_file.processed_file_path, finished=processed_file.finished,
                        request_id=processing_request.id, file_origin="processed"
                    ))
            return files

        all_user_requests = ProcessingFilesRequest.objects.filter(user_id=user_id)
        all_files = []
        for processing_request in all_user_requests:
            all_files += ___get_source_files(processing_request)
            all_files += ___get_processed_files(processing_request)

        all_files.reverse()
        return all_files


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

    class Meta:
        verbose_name_plural = 'Uploaded files'
