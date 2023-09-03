from django import forms

from plugin_system.plugin import Plugin
from plugin_system.plugin_form import PluginForm


class RenamePngPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name,
            ["image/png"],
            "plugin_system.plugins.minimal_plugin_example.plugin_config.RenamePngForm",
            "plugin_system.plugins.minimal_plugin_example.rename_task.RenamePngTask",
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type == "image/png":
            result.append("image/png")
        return result


class RenamePngForm(PluginForm):
    new_filename_prefix = forms.CharField(
        initial="new_",
        required=True
    )
