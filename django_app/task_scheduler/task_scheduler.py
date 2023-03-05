import pickle
import threading
import time
from datetime import datetime

from plugin_system.processing_classes.processing_exception import ProcessingException
from .db_con import get_connection


class TaskScheduler:
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
            "datetime DATETIME DEFAULT CURRENT_TIMESTAMP,"
            "exception VARCHAR NOT NULL DEFAULT ''"
            ")"
        )
        self.last_time = ""

    @classmethod
    def run_unfinished_tasks(cls) -> None:
        def ___load_task(query_row):
            task_obj = pickle.loads(query_row["object"])
            task_obj.task_id = query_row["id"]
            return task_obj

        response = cls.__get_unfinished_tasks()
        for task in [___load_task(obj) for obj in response]:
            if not task.finished:
                try:
                    task.run()
                    task.finish_task()
                except ProcessingException as e:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE task_objects SET exception = ? where `id` = ?;",
                        ("Something has gone wrong with this file: " + e.source_file.split("/")[-1], task.task_id)
                    )
                    conn.commit()
                    raise e.exception

    @classmethod
    def check_for_unfinished_tasks(cls) -> bool:
        if not cls.quiet_mode:
            print("checked db at " + str(datetime.now()))
        res = cls.__get_unfinished_tasks()
        return False if res is None else len(res) >= 1

    @classmethod
    def __get_unfinished_tasks(cls):
        cur = get_connection().cursor()
        return cur.execute("SELECT * FROM task_objects where finished=False;").fetchall()

    @staticmethod
    def __get_timestamp(time_string):
        return datetime.strptime(time_string, "%Y:%m:%d %h:%m:%s")


class TaskExecutorDaemon(threading.Thread):
    interval_in_seconds: int = 5

    @classmethod
    def start_async(cls, interval_in_seconds: int = 5):
        cls.interval_in_seconds = interval_in_seconds
        reader = cls(daemon=True)
        reader.start()

    def run(self):
        time.sleep(2)
        task_scheduler = TaskScheduler()
        print("started TaskScheduler.")
        while True:
            if task_scheduler.check_for_unfinished_tasks():
                task_scheduler.run_unfinished_tasks()
            time.sleep(self.interval_in_seconds)
