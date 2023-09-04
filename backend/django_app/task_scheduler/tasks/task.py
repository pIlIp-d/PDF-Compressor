import pickle
from abc import abstractmethod, ABC
from django_app.task_scheduler.db_con import get_connection


class Task(ABC):
    def __init__(self):
        self.task_id = None
        self.finished = False

    def create(self) -> int:
        connection = get_connection()
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO task_objects (object) VALUES(?);",
            (pickle.dumps(self),)
        )
        self.task_id = cur.lastrowid
        connection.commit()
        return self.task_id

    @abstractmethod
    def run(self): pass

    def finish_task(self):
        print("Finished task " + str(self.task_id))
        connection = get_connection()
        cur = connection.cursor()
        cur.execute(f"UPDATE task_objects SET finished = True WHERE id = ?;", (self.task_id,))
        connection.commit()
        self.finished = True
