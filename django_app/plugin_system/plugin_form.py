from django.forms import Form, RegexField


class PluginForm(Form):
    processing_file_extension = RegexField(
        regex="",  # TODO regex for allowed chars
        initial="compressed",
        label='Processing File Extension:',
        help_text='TODO'
    )

    def get_hierarchy(self) -> dict:
        return {}
