import pickle
from datetime import datetime
from .db_con import get_connection


class TaskScheduler:
    interval = None
    quiet_mode = True

    def __init__(self, quiet_mode: bool = True):
        self.quiet_mode = quiet_mode
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

    @classmethod
    def check_for_unfinished_tasks(cls) -> bool:
        if not cls.quiet_mode:
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
