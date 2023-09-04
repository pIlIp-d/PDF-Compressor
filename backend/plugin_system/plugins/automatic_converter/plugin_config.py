from django import forms

from plugin_system.plugin import Plugin
from plugin_system.plugin_form import PluginForm


class AutomaticConvertPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name,
            ["*"],
            "plugin_system.plugins.automatic_converter.plugin_config.AutomaticConvertForm",
            "plugin_system.plugins.automatic_converter.plugin_task.AutomaticConvertTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        result.append("*")
        return result


class AutomaticConvertForm(PluginForm):
    new_filetype = forms.CharField(
        initial=".",
        required=True
    )
