from django.forms import Form, RegexField


class PluginForm(Form):

    def get_hierarchy(self) -> dict:
        return {}
