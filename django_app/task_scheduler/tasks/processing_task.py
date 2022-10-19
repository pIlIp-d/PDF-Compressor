from abc import ABC

from django_app.task_scheduler.tasks.task import Task
from django_app.task_scheduler.event_handler.process_stats_event_handler import ProcessStatsEventHandler
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.models.uploaded_file import UploadedFile
from django_app.webserver.string_utility import StringUtility


# TODO document all options, destination_file is in [file, folder, merge, split]
class ProcessingTask(Task, ABC):
    def __init__(
            self,
            request_parameters: dict,
            processing_request: ProcessingFilesRequest
    ):
        super().__init__()
        self._request_id = processing_request.id
        self._request_parameters = request_parameters
        self._source_path = StringUtility.get_local_absolute_path(processing_request.get_source_dir())
        # destination is either merged file or directory
        self._destination_path = "merge" if self._request_parameters.get("merge_files") else \
            StringUtility.get_local_absolute_path(processing_request.get_destination_dir())
        self.__amount_of_input_files = len(
            UploadedFile.get_uploaded_file_list_of_current_request(processing_request)
        )

    def _get_event_handler(self) -> list[ProcessStatsEventHandler]:
        return [
            ProcessStatsEventHandler(self._request_id)
        ]
