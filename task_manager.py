from time import sleep

from django_app.task_scheduler.task_scheduler import TaskScheduler

INTERVAL_TIME = 5
QUIET_MODE = False


if __name__ == "__main__":
    task_scheduler = TaskScheduler()
    while True:
        if task_scheduler.check_for_unfinished_tasks():
            task_scheduler.run_unfinished_tasks()
        sleep(INTERVAL_TIME)
