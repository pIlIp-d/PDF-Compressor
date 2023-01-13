import os
from abc import ABC

from django_app.settings import MEDIA_ROOT
from django_app.task_scheduler.tasks.task import Task
from django_app.task_scheduler.processing_event_handler import ProcessingEventHandler
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest


class ProcessingTask(Task, ABC):
    def __init__(
            self,
            request_parameters: dict,
            processing_request: ProcessingFilesRequest
    ):
        super().__init__()
        self._request_id = processing_request.id
        self._request_parameters = request_parameters
        self._source_path = os.path.join(MEDIA_ROOT, processing_request.get_source_dir())
        # destination is either merged file or directory
        self._destination_path = "merge" if self._request_parameters.get("merge_files") else \
            os.path.join(MEDIA_ROOT, processing_request.get_destination_dir())  # TODO TODO TODO replace with only "merge" or "default"

    def _get_event_handler(self) -> list[ProcessingEventHandler]:
        return [
            ProcessingEventHandler(self._request_id)
        ]
