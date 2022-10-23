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

## start the web-app

`python3 manage.py runserver`

_____

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

# Plugins

## Add a new Plugin

* add a folder to `<project>/plugins/<your_plugin>`
* add a [Plugin subclass](#Plugin-Class)
* add a [ProcessingTask subclass](#Processing-Task)
* add a [Plugin Form](#Plugin-Form)
* add the reference inside `<project>/django_app/settings.py` -> `PROCESSOR_PLUGINS`

## Plugin Class

1. add constructor with all parameters to super call
2. add a get_destination_types implementation

### Examples
an implemented example can be found in `plugins/minimal_plugin_example/`

```python
from django_app.plugin_system.plugin import Plugin


class ExamplePlugin(Plugin):
    # example plugin declaration for converting from
    # pdf -> svg
    def __init__(self, name: str):
        super().__init__(
            name=name,
            from_file_types=["image/png"],  # list of possible mime types (https://mimetype.io/all-types/)
            form="plugins.example_plugin.example_plugin_form.PdfCompressorForm",
            task="plugins.example_plugin.example_plugin_task.PdfCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        # super call required
        result = super().get_destination_types(from_file_type)
        # add a result file type if the from_file_type fits a certain mime-type
        if from_file_type == "image/png":
            result.append("image/svg")
        return result

    # optionally implement own get_form_html_and_script()
```

## Processing Task

```python
from django_app.task_scheduler.tasks.processing_task import ProcessingTask


class ExampleTask(ProcessingTask):
  def run(self):
    event_handler = super()._get_event_handler()
    ###################
    # run your processing, converting, compressing etc
    #  use parameters in self._request_parameters: dict, contains all parameters from your Form
    example_int_parameter = int(self._request_parameters.get("example_int_parameter"))
    example_checkbox_parameter = self._request_parameters.get("example_checkbox_parameter") == "on"
    example_string_parameter = self._request_parameters.get("example_string_parameter")
    
    # optionally use a Processor subclass for your file processing
    
    #  see event_handler documentation, so that you trigger all necessary events
    #  optionally follow `settings.DEBUG` for your quiet mode/ print suppressing
    ###################
```
### Event Handler Class

every task should trigger certain events, that can be used by the program to determine progress or to apply different processing like zipping or console logging

```python
class EventHandler(...):
    # is called before your processing task starts
    def started_processing(self): pass
    # is called after all processing has been finished and the result files exist in the destination directory
    def finished_all_files(self): pass
    # call before each processing of a file
    def preprocess(self, source_file: str, destination_file: str) -> None: pass
    # call after each processing of a file has been finished with source_file as the unchanged starting file
    # and destination_file the processed file
    def postprocess(self, source_file: str, destination_file: str) -> None: pass
```


## Plugin Form

* `help_text` - is shown on html form when you hover over the given form field
* `initial` - default value of a field when form is loaded in the website

```python
from django import forms
from django_app.plugin_system.plugin_form import PluginForm


class ExampleForm(PluginForm):
    example_choice_field = forms.TypedChoiceField(
        label='Example Choice Field:',
        choices=(
            ("1", 'English'),
            ("2", 'Deutsch'),
        ),
        coerce=str,
        initial="1",
        help_text='Describe your option'
    )
    example_int_field = forms.IntegerField(
        label='Example Int Field:',
        min_value=10,
        max_value=1000,
        step_size=10,
        required=True,
        initial=400,
        help_text='Describe your option'
    )
    example_bool_field = forms.BooleanField(
        label='Example Bool Field:',
        initial=True,
        help_text="Describe your option"
    )
    example_text_field = forms.RegexField(
        label='Example Text Field:',
        regex="",  # leave empty if not used
        initial="start_value",
        help_text='Describe your option'
    )
# optionally implement get_hierarchy()
```

### Prototype Form Fields

Fields that can be used for your form and that have functionality partially implemented already

```python
# creates a single output file Object (good for download view)
merge_files = forms.BooleanField(
    label='Merge files into a single output File.',
    initial=False,
    help_text="TODO"
)
```

### PluginForm.get_hierarchy()

Define hierarchy to deactivate options depending on the state of other options
returns a dictionary

```json
{
  "example_parent_field": {
    "type": "bool",
    "hide_state": "True",
    "children": [
      "..."
    ]
  },
  "example_choice_field": {
    "type": "choice",
    "values_for_deactivation": [
      "1"
    ],
    "children": [
      "..."
    ]
  }
}
```

Per parent there are required fields

| type             | required_parameters      | values    | description                                        |
|------------------|--------------------------|-----------|----------------------------------------------------|
| required for all | children                 | list[str] | all names of children, that are meant to hide      |
|                  |                          |           |                                                    |
| bool             | hide_state               | 'False'   | hide children when deactivated (unchecked)         |
|                  |                          | 'True'    | hide children when activated (checked)             |
|                  |                          |           |                                                    |
| choice           | values_for_deactivation  | list[str] | list of all values, that should trigger the hiding |
|                  |                          |           |                                                    |


# TODOs

* **add remove all files button (per User) to download page**
* **POST value validating with django forms (inside webserver/views.py)**
* /media folder memory management (capacity per user etc.)
* GarbageCollector (regular cleanup of old Tasks, /media folder, /temporary_files folder)
  * deletes request, if it has no files
* option reserve/strip meta data
* option bookmarks
* download view delete button per request (deletes corresponding request, tasks and files)
* POST value validating with django forms
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
