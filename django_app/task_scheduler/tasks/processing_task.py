import os
import shutil
from abc import ABC

from django_app.settings import MEDIA_ROOT
from django_app.task_scheduler.tasks.task import Task
from django_app.task_scheduler.processing_event_handler import ProcessingEventHandler
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.models.uploaded_file import UploadedFile


class ProcessingTask(Task, ABC):
    def __init__(
            self,
            request_parameters: dict,
            processing_request: ProcessingFilesRequest,
            files: list[UploadedFile]
    ):
        super().__init__()
        self._request_id = processing_request.id
        self._request_parameters = request_parameters
        self._source_path = os.path.join(MEDIA_ROOT, processing_request.get_source_dir())

        os.mkdir(self._source_path)
        for file in files:
            print(file.id)
            print(os.path.join(MEDIA_ROOT, file.uploaded_file.name), self._source_path)
            shutil.move(os.path.join(MEDIA_ROOT, file.uploaded_file.name), self._source_path)

        # destination is either merged file or directory
        self._destination_path = "merge" if self._request_parameters.get("merge_files") else "default"

    def _get_event_handler(self) -> list[ProcessingEventHandler]:
        return [
            ProcessingEventHandler(self._request_id)
        ]
