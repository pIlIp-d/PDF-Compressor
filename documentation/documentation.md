# Django App

_____
## set up the django project
cd into the Project directory

makemigration, migrate

## start the web-app
`python3 manage.py runserver`
## start the processing daemon
`python3 task_manager.py`

_____
# How it works

## django webapp (UI nd Backend)

the django python package is used as webserver.  
It displays the website, handles requests and forwards the processing request to the task_scheduler.

## Processing (Backend)

The taskScheduler class checks for changes in the tasks db and if changes are detected,  
it starts processing (i.e Compressing) by using the data/parameters given in the tasks.tasks db table.

## New Tasks

can be added to the queue by instantiating a Task subclass from any Thread.
required parameters can be found in Task parent class.
It works by creating a db entry in tasks.db tasks table, which is then executed by the task_scheduler.

``
``
``
``
