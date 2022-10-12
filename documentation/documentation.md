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

# Plugins

## Add a new Plugin

* add a folder to `<project>/plugins/<your_plugin>`
* add a [Plugin subclass](#_Plugin_Class)
* add a [ProcessingTask subclass](#_Processing_Task)
* add a [Plugin Form](#_Plugin_Form)
* add the reference inside `<project>/django_app/settings.py` `PROCESSOR_PLUGINS`

## Plugin Class

1. add constructor with all parameters to super call
2. add a get_destination_types implementation

Examples

```python
from django_app.plugin_system.plugin import Plugin


class ExamplePlugin(Plugin):
    # example plugin declaration for converting from
    # pdf -> jpg, 
    def __init__(self, name: str):
        super().__init__(
            name=name,
            from_file_types=["pdf", "png", "jpg", "jpeg"],
            form="plugins.example_plugin.example_plugin__form.PdfCompressorForm",
            task="plugins.example_plugin.example_plugin_task.PdfCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        # super call required
        result = super().get_destination_types(from_file_type)
        if from_file_type == "png":
            result.append("svg")
        elif from_file_type == "pdf":
            result.append("jpg")
        elif from_file_type == "jpg" or from_file_type == "jpeg":
            result.append("png")
        return result

    # optionally implement own get_form_html_and_script()
```

## Processing Task

```python
from django_app.task_scheduler.tasks.processing_task import ProcessingTask


class ExampleTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_process_stats_event_handler()
        ###################
        # run your processing, converting, compressing etc
        #  use parameters in self._request_parameters: dict, contains all parameters from your Form
        example_int_parameter = int(self._request_parameters.get("example_int_parameter"))
        example_checkbox_parameter = self._request_parameters.get("example_checkbox_parameter") == "on"
        example_string_parameter = self._request_parameters.get("example_string_parameter")

        #  see event_handler documentation, so that you trigger all necessary events
        #  optionally follow `settings.DEBUG` for your quiet mode/ print suppressing
        ###################
```

## Plugin Form

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

### prototype form fields

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

per parent there are required fields

| type             | required_parameters      | values    | description                                        |
|------------------|--------------------------|-----------|----------------------------------------------------|
| required for all | children                 | list[str] | all names of children, that are meant to hide      |
|                  |                          |           |                                                    |
| bool             | hide_state               | 'False'   | hide children when deactivated (unchecked)         |
|                  |                          | 'True'    | hide children when activated (checked)             |
|                  |                          |           |                                                    |
| choice           | values_for_deactivation  | list[str] | list of all values, that should trigger the hiding |
|                  |                          |           |                                                    |

# Event Handler Class

every tasks should trigger certain events, that can be used by the program to determine progress or to apply different processing like zipping or console logging

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

# TODOs

* /media folder memory management (capacity per user etc)
* GarbageCollector (regular cleanup of old Tasks, /media folder, /temporary_files folder)
  * deletes request, if it has no files
* add remove all files button (per User)
* using **kwargs, read-only, password
* option reserve/strip meta data
* option bookmarks
* [!] mime Type check instead of file ending only (with 'python-magic' package)
* POST value validating with django forms (inside ProcessingTasks)
* download view delete button per request (deletes corresponding request, tasks and files)
* POST value validating with django forms
* unittest with file_ending not all small chars
* unittest with more than 1, 10, 100 sites

* check options via imagemagick tool

# Plugin Ideas
* make compression plugin for pdf with password using cpdf
* combinations of PSD files
* OpenCV implementations
* 