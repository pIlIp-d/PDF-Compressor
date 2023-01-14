# Plugins

## Add a new Plugin

1. add a folder to `<project>/plugins/<your_plugin>`
2. add a [Plugin subclass](#Plugin-Class)
3. add a [ProcessingTask subclass](#Processing-Task)
4. add a [Plugin Form](#Plugin-Form)
5. add the reference inside `<project>/django_app/settings.py` -> `PROCESSOR_PLUGINS`

## Plugin Class

1. add constructor with all parameters to super call
2. add a get_destination_types implementation

an implemented example can be found in `plugins/minimal_plugin_example/`

```python
from plugin_system.plugin import Plugin


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
### Processor
make file-processing much simpler by using the [Processor](../plugin_system/processing_classes/processor.py) class

```python
"from plugin_system.processing_classes.processor import Processor


class MyProcessor(Processor):
    def __init__(self, event_handlers: list):
        super().__init__(
            event_handlers,
            # insert your allowed file endings
            file_type_from=[".input_example1", ".example2", ".pdf"],
            file_type_to=".result_example"
        )

    # you only need to implement process_file to enable processing for folders, files, etc 
    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        #################
        # your processing
        #################
        self.preprocess(source_file, destination_path)

    # optionally you can implement _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
    # to enable merging of a folder into a single file
```


## Plugin Form

* `help_text` - is shown on html form when you hover over the given form field
* `initial` - default value of a field when form is loaded in the website

```python
from django import forms
from plugin_system.plugin_form import PluginForm


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

IMPORTANT on choiceFields you need to have a comma after the last option inside choices
```
name = forms.TypedChoiceField(
        choices=(
            ('value', 'shown Value'), <---
        ),
        ...
```

## Prototype Form Fields

Fields that can be used for your form and that have functionality partially implemented already

```python
# creates a single output file Object (good for download view)
merge_files = forms.BooleanField(
    label='Merge files into a single output File.',
    initial=False,
    help_text="TODO"
)
```

## PluginForm.get_hierarchy()

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

