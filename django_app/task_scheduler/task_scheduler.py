import sys
from datetime import datetime

import jsons

from .db_con import get_connection, fetch_all_as_dict

# for every task type the import must be correct and the exact Classname must be used as task_type
from .pdf_compression_task import PdfCompressionTask
SUPPORTED_TASK_TYPES = ["PdfCompressionTask"]

QUIET_MODE = False


class TaskScheduler:
    interval = None

    def __init__(self):
        # create db table if not exists
        connection = get_connection()

        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks("
            "id INTEGER primary key autoincrement,"
            "request_id INTEGER NOT NULL,"
            "task_type TEXT NOT NULL,"
            "parameters JSON NOT NULL,"
            "datetime datetime DEFAULT CURRENT_TIMESTAMP,"
            "finished BOOL DEFAULT 0"
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
        res = cur.execute("SELECT * FROM tasks where finished=False;").fetchone()
        return False if res is None else len(res) >= 1

    @classmethod
    def get_tasks(cls) -> list:
        try:
            def ___get_task(task):
                if task["task_type"] not in SUPPORTED_TASK_TYPES:
                    raise ValueError("Task type invalid!")
                print(jsons.loads(task["parameters"]))
                return globals()[task["task_type"]](**jsons.loads(task["parameters"]), task_id=task["id"], request_id=task["request_id"], finished=task["finished"])
            return [___get_task(task) for task in cls._get_raw_tasks()]

        except AttributeError as e:
            return []

    @classmethod
    def _get_raw_tasks(cls, task_type: str = "all"):
        cur = get_connection().cursor()
        special = "" if task_type == "all" else f" WHERE task_type = {task_type}"
        res = cur.execute(f"SELECT * FROM tasks{special};")
        return fetch_all_as_dict(res)
