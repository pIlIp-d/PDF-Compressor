from django.forms import Form


class PluginForm(Form):

    def get_hierarchy(self) -> dict:
        return {}

    def get_advanced_options(self) -> list[str]:
        return []
