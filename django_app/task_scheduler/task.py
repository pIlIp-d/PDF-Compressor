from abc import abstractmethod

import jsons

from django_app.task_scheduler.db_con import get_connection


class Task:
    def __init__(self, request_id: int, task_type: str, task_id: int = None, finished: bool = False, **parameters):
        self.request_id = request_id
        self.task_type = task_type
        self.task_id = task_id
        self.finished = finished
        self._parameters = dict()
        for key, value in parameters.items():
            self._parameters[key] = value
        if self.task_id is None:
            self._add()

    def _add(self):
        connection = get_connection()
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO tasks (request_id, task_type, parameters) VALUES(?, ?, ?);",
            (self.request_id, self.task_type, jsons.dumps(self._parameters),))
        self.task_id = cur.lastrowid
        connection.commit()

    @abstractmethod
    def run(self): pass

    def finish_task(self):
        connection = get_connection()
        cur = connection.cursor()
        print(self.task_id)
        cur.execute(f"UPDATE tasks SET finished = True WHERE id = ?;", (self.task_id, ))
        connection.commit()

