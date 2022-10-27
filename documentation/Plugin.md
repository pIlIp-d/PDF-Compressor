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

! on choiceFields you need to have a comma after the last option inside choices
```
name = forms.TypedChoiceField(
        choices=(
            ('value', 'shown Value'), <---
        ),
        ...
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

