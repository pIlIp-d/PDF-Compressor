#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys

PORT = "8080"
ADDRESS = "0.0.0.0"
METHOD = "http"


def configure():
    from django.core.management.commands.runserver import Command as Server
    Server.default_addr = ADDRESS
    Server.default_port = PORT


def main():
    if sys.argv[1] == "runserver":
        configure()
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
