from functools import reduce
import os
from abc import ABC
from django_app.task_scheduler.tasks.task import Task
from django_app.webserver.custom_models.process_stats_event_handler import ProcessStatsEventHandler
from django_app.webserver.custom_models.zip_all_files_event_handler import ZipAllFilesEventHandler


class ProcessingTask(Task, ABC):

    def __init__(self, request_id: int, amount_of_input_files: int, processed_file_paths: list,
                 task_id: int = None, finished: bool = False,
                 **parameters):
        parameters["amount_of_input_files"] = amount_of_input_files
        parameters["processed_file_paths"] = processed_file_paths
        super().__init__(request_id, task_id, finished, **parameters)

    def _get_process_stats_event_handler(self) -> list[ProcessStatsEventHandler]:
        # remove extra args from parameters
        amount_of_input_files = self._parameters["amount_of_input_files"]
        processed_file_paths = self._parameters["processed_file_paths"]
        self._parameters = {key: value for key, value in self._parameters.items() if
                            key not in ("amount_of_input_files", "processed_file_paths")}

        return [
            ZipAllFilesEventHandler(
                processed_file_paths[0]
            ),
            ProcessStatsEventHandler(
                amount_of_input_files,
                processed_file_paths,
                self.request_id
            )
        ]
