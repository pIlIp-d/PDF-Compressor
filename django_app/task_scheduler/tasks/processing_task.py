from abc import ABC, abstractmethod
from django_app.task_scheduler.tasks.task import Task
from django_app.webserver.custom_models.process_stats_event_handler import ProcessStatsEventHandler
from django_app.webserver.custom_models.string_utility import StringUtility
from django_app.webserver.custom_models.zip_all_files_event_handler import ZipAllFilesEventHandler
from django_app.webserver.models import ProcessingFilesRequest


class ProcessingTask(Task, ABC):
    def __init__(
            self,
            request_parameters: dict,
            processing_request: ProcessingFilesRequest,
            processed_file_paths: list
    ):
        super().__init__(processing_request.id)
        self._request_parameters = request_parameters
        self.__source_path = StringUtility.get_local_absolute_path(processing_request.get_source_dir())
        # destination is either merged file or directory
        self.__destination_path = StringUtility.get_local_absolute_path(
            processed_file_paths[-1] if request_parameters.get(
                "merge_files") else processing_request.get_destination_dir()
        )
        self.__amount_of_input_files = len(
            ProcessingFilesRequest.get_uploaded_file_list_of_current_request(processing_request)
        )
        self.__processed_file_paths = processed_file_paths

    def _get_process_stats_event_handler(self) -> list[ProcessStatsEventHandler]:
        return [
            ZipAllFilesEventHandler(
                self.__processed_file_paths[0]
            ),
            ProcessStatsEventHandler(
                self.__amount_of_input_files,
                self.__processed_file_paths,
                self._request_id
            )
        ]
