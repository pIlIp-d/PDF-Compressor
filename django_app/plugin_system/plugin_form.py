from django.forms import Form


class PluginForm(Form):

    def get_hierarchy(self) -> dict:
        return {}
