"""
WSGI config for django_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

from django_app import settings
from django_app.task_scheduler.task_scheduler import TaskExecutorDaemon

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
application = get_wsgi_application()
TaskExecutorDaemon.start_async()

# validate plugin imports
try:
    for plugin in settings.PROCESSOR_PLUGINS:
        plugin.get_form_class()
        plugin.get_task()
    print("Loaded plugins successfully.")
except ImportError as e:
    if settings.DEBUG:
        raise e
    print(str(e), file=sys.stderr)
