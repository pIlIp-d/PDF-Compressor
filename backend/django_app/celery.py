import os


from celery import Celery
from django_app import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')


app = Celery('django_app',
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0',
             include=[".".join(plugin.task.split(".")[:-1]) for plugin in settings.PROCESSOR_PLUGINS]
             )

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

# Using a string here means the worker doesn’t have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
