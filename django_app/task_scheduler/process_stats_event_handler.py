import requests

import manage
from django_app.plugin_system.processing_classes.event_handler import EventHandler


class ProcessingEventHandler(EventHandler):
    def __init__(self, request_id: int):
        super().__init__()
        self.__request_id = request_id

    def started_processing(self):
        self.__make_request("api/started_processing/")

    def finished_all_files(self):
        self.__make_request("api/finished_all_files/")

    def __make_request(self, path):
        status = requests.get(f"{manage.METHOD}://localhost:{manage.PORT}/" + path,
                              {"request_id": self.__request_id})
        if status.status_code != 200:
            raise ConnectionError(status)
