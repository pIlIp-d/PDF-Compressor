# Django App

### Table of Content
1. [Frontend](#Django-Webapp-(UI-and-Backend))
2. [Backend](#Processing-(Backend))
3. [Plugins](#Plugins)
   1. [Add a new Plugin](#Add-a-new-Plugin)
      1. [Plugin Class](#Plugin-Class)
      2. [Processing Task](#Processing-Task)
         1. [Event Handler Class](#Event-Handler-Class)
      3. [Plugin Form](#Plugin-Form)
4. [TODOs](#TODOs)

_____

# System Overview
![All Components and Relations](components.puml)

## UML diagrams
diagrams are using the PlantUML integration plugin / syntax  
syntax can be found here: [https://plantuml.com](https://plantuml.com)

# How it works

## django webapp (UI nd Backend)

the django python package is used as webserver.  
It displays the website, handles requests and forwards the processing request to the task_scheduler.

* `django_app/webserver` holds the views for user interaction
* `django_app/api` holds the views that deliver data to js or handle form-requests

## Processing (Backend)

The taskScheduler class checks for changes in the tasks db and if changes are detected,  
it starts processing (e.g. Compressing) by using the data/parameters given in the `tasks.tasks` db table.

## New Tasks

A Task can be added by constructing a subclass of `django_app.task_scheduler.tasks.task.Task` and call the create() method.
After that the `Task.run()` method is executed automatically.

It works by creating a db entry in tasks.db tasks table, which is then executed by the task_scheduler.

### **ProcessingTask**
Is a Task class that is used for File Request Processing (mainly of the plugins).  
Delivers default `_source_path`, `_destination_path`, `_request_parameters` attributes to subclasses.
These values can be used to run `<Processor>.process()` for your Plugin.  
`_request_parameters` includes all form parameters of your custom form.

# TODOs

* **add remove all files button (per User) to download page**
* Selenium Tests
* POST value validating with django forms (inside webserver/views.py)**
* /media folder memory management (capacity per user etc.)
* GarbageCollector (regular cleanup of old Tasks, /media folder, /temporary_files folder)
  * deletes request, if it has no files
* option reserve/strip meta data
* option bookmarks
* download view delete button per request (deletes corresponding request, tasks and files)
* unittest with file_ending not all small chars
* unittest with more than 1, 10, 100 sites
* display errors in processing in the download view or somewhere else

* check options via imagemagick tool
* Online Admin view for Files, Requests etc, maybe some config stuff (like time how long files are saved etc)

https://mimetype.io/all-types/

# Plugin Ideas
* make compression plugin for pdf with password using cpdf
* combinations of PSD files
* OpenCV implementations
