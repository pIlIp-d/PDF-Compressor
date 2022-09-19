from time import sleep

from django_app.task_scheduler.task_scheduler import TaskScheduler

INTERVAL_TIME = 5

# todo create socket that is called from task constructor instead if timer loop
if __name__ == "__main__":
    task_scheduler = TaskScheduler()
    while True:
        if task_scheduler.check_for_unfinished_tasks():
            task_scheduler.run_unfinished_tasks()
        sleep(INTERVAL_TIME)
