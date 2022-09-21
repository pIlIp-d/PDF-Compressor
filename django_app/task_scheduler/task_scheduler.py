import pickle
from datetime import datetime


from .db_con import get_connection, fetch_all_as_dict

QUIET_MODE = False


class TaskScheduler:
    interval = None

    def __init__(self):
        # create db table if not exists
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS task_objects("
            "id INTEGER primary key autoincrement,"
            "object TEXT NOT NULL,"
            "finished BOOL DEFAULT 0,"
            "datetime DATETIME DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        self.last_time = ""

    @classmethod
    def run_unfinished_tasks(cls):
        open_tasks = [task for task in cls.get_tasks() if not task.finished]
        for task in open_tasks:
            task.run()

    @staticmethod
    def __get_timestamp(time_string):
        return datetime.strptime(time_string, "%Y:%m:%d %h:%m:%s")

    @staticmethod
    def check_for_unfinished_tasks() -> bool:
        if not QUIET_MODE:
            print("checked db at " + str(datetime.now()))
        cur = get_connection().cursor()
        res = cur.execute("SELECT * FROM task_objects where finished=False;").fetchone()
        return False if res is None else len(res) >= 1

    @classmethod
    def get_tasks(cls) -> list:
        def __load_task(query_row):
            task = pickle.loads(query_row["object"])
            task.task_id = query_row["id"]
            return task

        cur = get_connection().cursor()
        response = cur.execute("SELECT * FROM task_objects where finished=False;").fetchall()
        return [__load_task(obj) for obj in response]
