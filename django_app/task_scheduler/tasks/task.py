import pickle
from abc import abstractmethod, ABC
from django_app.task_scheduler.db_con import get_connection


class Task(ABC):
    def __init__(self):
        self._task_id = None
        self.finished = False

    def create(self):
        connection = get_connection()
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO task_objects (object) VALUES(?);",
            (pickle.dumps(self),)
        )
        self._task_id = cur.lastrowid
        connection.commit()

    @abstractmethod
    def run(self): pass

    def finish_task(self):
        print("Finished task " + str(self._task_id))
        connection = get_connection()
        cur = connection.cursor()
        cur.execute(f"UPDATE task_objects SET finished = True WHERE id = ?;", (self._task_id,))
        connection.commit()
        self.finished = True
