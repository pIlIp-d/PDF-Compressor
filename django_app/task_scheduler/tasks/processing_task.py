from abc import ABC
from django_app.task_scheduler.tasks.task import Task
from django_app.webserver.custom_models.process_stats_event_handler import ProcessStatsEventHandler
from django_app.webserver.custom_models.zip_all_files_event_handler import ZipAllFilesEventHandler
from django_app.webserver.models import ProcessingFilesRequest


class ProcessingTask(Task, ABC):
    def __init__(
            self,
            processing_request: ProcessingFilesRequest,
            processed_file_paths: list,
            task_id: int = None,
            finished: bool = False
    ):
        super().__init__(processing_request.id, task_id, finished)
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
