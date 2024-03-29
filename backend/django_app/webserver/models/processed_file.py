import os

from django.db import models

from django_app.settings import TIME_FORMAT, MEDIA_ROOT
from django_app.task_scheduler.db_con import get_connection
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.models.uploaded_file import UploadedFile


class ProcessedFile(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True, serialize=False, verbose_name='ID')
    processing_request = models.ForeignKey(ProcessingFilesRequest, on_delete=models.CASCADE)
    processed_file_path = models.TextField()
    date_of_upload = models.DateTimeField(auto_now_add=True)
    merger = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ": " + str(self.processed_file_path)

    def delete(self, using=None, keep_parents=False):
        def file_count():
            return len(UploadedFile.objects.filter(processing_request=self.processing_request)) \
                + len(ProcessedFile.objects.filter(processing_request=self.processing_request))

        file = str(self.processed_file_path)
        if os.path.isfile(file):
            os.remove(file)
        if file_count() <= 1:
            self.processing_request.delete()
        super(ProcessedFile, self).delete(using, keep_parents)

    class Meta:
        verbose_name_plural = 'Processed files'

    @classmethod
    def add_processed_file(cls, processed_file_path: str, processing_request: ProcessingFilesRequest):
        processed_file = cls(
            processed_file_path=processed_file_path,
            processing_request=processing_request
        )
        processed_file.save()
        return processed_file

    @classmethod
    def get_all_processing_files(cls, user_id: str, request_id: str = None):
        def ___get_json(file_obj, filename: str, filename_path: str, request_id: int, file_origin: str, exception: str):
            abs_file_path = os.path.join(MEDIA_ROOT, filename_path)
            file_is_present = os.path.isfile(abs_file_path)
            return {
                "file_id": file_obj.id,
                "filename": os.path.basename(filename),
                "filename_path": os.path.join("media", filename_path),
                "finished": file_is_present,
                "request_id": request_id,
                "date_of_upload": file_obj.date_of_upload.strftime(TIME_FORMAT),
                "file_origin": file_origin,
                "size": 0 if not file_is_present else os.path.getsize(abs_file_path),
                "exception": exception
            }

        def ___get_source_files(___processing_request):
            files = []
            for file in UploadedFile.objects.filter(processing_request=___processing_request).order_by(
                    'date_of_upload'):
                files.append(___get_json(
                    file_obj=file, filename=file.uploaded_file.name + " (Original)",
                    filename_path=file.uploaded_file.name, request_id=___processing_request.id,
                    file_origin="uploaded",
                    exception=___get_task_exceptions(___processing_request.task_id)
                ))
            return files

        def ___get_task_exceptions(task_id: int):
            cur = get_connection().cursor()
            exception = cur.execute("SELECT exception FROM task_objects where `id` = ?;", (task_id,)).fetchone()
            return "" if exception is None else exception[0]

        def ___get_processed_files(___processing_request):
            files = []
            for processed_file in ProcessedFile.objects.filter(processing_request=___processing_request).order_by(
                    'date_of_upload'):  # TODO reverse
                if processed_file.processing_request.id == ___processing_request.id:
                    files.append(___get_json(
                        file_obj=processed_file, filename=processed_file.processed_file_path,
                        filename_path=processed_file.processed_file_path,
                        request_id=___processing_request.id, file_origin="processed",
                        exception=___get_task_exceptions(processed_file.processing_request.task_id)
                    ))
            return files

        args = {"user_id": user_id}
        if request_id is not None:
            args["id"] = request_id
        all_user_requests = ProcessingFilesRequest.objects.filter(**args)
        all_files = []
        for processing_request in all_user_requests:
            all_files += ___get_source_files(processing_request)
            all_files += ___get_processed_files(processing_request)

        all_files.reverse()
        return all_files
