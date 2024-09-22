#!/bin/sh
cd backend

python manage.py migrate
python3 manage.py runserver &

celery -A django_app worker --loglevel=INFO

wait