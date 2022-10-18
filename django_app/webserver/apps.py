from django.apps import AppConfig

from django_app.task_scheduler.task_scheduler import TaskSchedulerDaemon


class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_app.webserver'

