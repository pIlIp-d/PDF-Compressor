import datetime
import os

from django_app.task_scheduler.tasks.zip_task import ZipTask
from django_app.webserver.models.processed_file import ProcessedFile
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.string_utility import StringUtility
from django_app.utility.event_handler import EventHandler
from django_app.utility.os_utility import OsUtility


# TODO rename to ProcesEventHandler
class ProcessStatsEventHandler(EventHandler):
    def __init__(self, request_id: int):
        super().__init__()
        self.__request_id = request_id

    def started_processing(self):
        processing_request = ProcessingFilesRequest.get_request_by_id(self.__request_id)
        processing_request.started = True
        processing_request.save()

    def finished_all_files(self):
        processing_request = ProcessingFilesRequest.get_request_by_id(self.__request_id)
        processing_request.finished = True
        processing_request.save()

        folder = StringUtility.get_local_absolute_path(
            os.path.join("uploaded_files", processing_request.user_id, str(processing_request.id) + "_processed")
        )
        zip_path = os.path.join(
            folder, "processed_files_" + StringUtility.get_formatted_time(datetime.datetime.now()) + ".zip"
        )
        os.makedirs(folder, exist_ok=True)

        # run synchronize
        ZipTask(folder, zip_path).run()

        # add files to download view
        for file in reversed(OsUtility.get_file_list(folder)):
            ProcessedFile.add_processed_file(StringUtility.get_media_normalized_path(file), processing_request)
