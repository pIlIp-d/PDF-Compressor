import os
import os.path
import pathlib
from django.db import models
from jsons import ValidationError


#  Depending on the attributes of the file gets stored in a different directory
def get_directory_to_save_file_in(instance, filename: str) -> str:
    # todo use request_queue id for file path, because it is getting too long (id from csrf_token) new Model=processing_request

    path = os.path.join("uploaded_files", f"user{instance.user_id}", instance.csrf_token[:10], filename)
    if os.path.isfile(os.path.join(".", "media", path)):
        os.chdir(path)
        for current_file in sorted(os.listdir(path)):  # rename
            print(current_file)

    extension_of_file = pathlib.Path(path).suffixes[-1].lower()
    if extension_of_file != '.pdf':
        raise ValidationError("Invalid extension. Only PDF-File's are allowed.")

    file_size = instance.uploaded_file.size
    if file_size > UploadedFile.MAX_FILESIZE:
        raise ValidationError("The maximum file size is reached.")

    return path


class UploadedFile(models.Model):
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    uploaded_file = models.ImageField(upload_to=get_directory_to_save_file_in)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


    def __str__(self):
        return str(self.pk) + ": " + str(self.uploaded_file.name)

    class Meta:
        verbose_name_plural = 'Uploaded files'


def get_file_list_of_current_request(request_id):
    return UploadedFile.objects.filter(
        processing_request=get_request_by_id(request_id)
    )


def start_process(request_id):
    request = get_request_by_id(request_id)
    request.started = True
    request.save()


def get_request_id(user_id: str, queue_csrf_token: str) -> int:
    return get_or_create_new_request(user_id, queue_csrf_token).id or -1


def get_request_by_id(request_id: int) -> ProcessingFilesRequest:
    return ProcessingFilesRequest.objects.filter(
        id=request_id
    ).first()


def get_or_create_new_request(user_id: str, queue_csrf_token: str) -> ProcessingFilesRequest:
    processing_request = ProcessingFilesRequest.objects.filter(
        user_id=user_id,
        csrf_token=queue_csrf_token
    ).first()
    if processing_request is None:
        ProcessingFilesRequest(
            user_id=user_id,
            csrf_token=queue_csrf_token
        ).save()
        processing_request = get_or_create_new_request(user_id, queue_csrf_token)
    return processing_request


class ProcessStatsProcessor(Preprocessor, Postprocessor):
    def __init__(self, files_to_process: list, request: ProcessingFilesRequest):
        super().__init__()
        self.__files_to_process = files_to_process
        self.__finished_files = 0
        self.__request = request
        request.started = True
        request.save()

    def get_progress(self):
        return self.__finished_files / len(self.__files_to_process)

    def preprocess(self, source_file: str, destination_file: str) -> None:
        print("preprocessing", source_file, destination_file)
        pass

    def postprocess(self, source_file: str, destination_file: str) -> None:
        print("postprocessing", source_file, destination_file)
        self.__finished_files += 1
        for file in self.__files_to_process:
            if source_file == os.path.abspath(os.path.join(MEDIA_FOLDER_PATH, file.uploaded_file.name)):
                file.finished = True
                file.save()
        if self.get_progress() == 1:
            self.__request.finished = True
            self.__request.save()
