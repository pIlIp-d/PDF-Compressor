from django import forms

from django_app.plugin_system.plugin_form import PluginForm


class PdfCompressorForm(PluginForm):
    merge_files = forms.BooleanField(
        label='Merge files into a single PDF.',
        initial=False,
        help_text="TODO"
    )
    processing_file_extension = forms.RegexField(
        regex="",  # TODO regex for allowed chars
        initial="compressed",
        label='Processing File Extension:',
        help_text='TODO'
    )
    simple_and_lossless = forms.BooleanField(
        label='Simple and lossless:',
        initial=True,
        help_text="TODO"
    )
    compression_mode = forms.TypedChoiceField(
        choices=(
            (1, '1: Extreme'),
            (2, '2: Strong'),
            (3, '3: Medium'),
            (4, '4: Fast'),
            (5, '5: Normal'),
        ),
        initial=5,
        label='Compression mode:',
        coerce=str,
        help_text='TODO'
    )
    default_pdf_dpi = forms.IntegerField(
        label='Default DPI:',
        min_value=10,
        max_value=1000,
        step_size=10,
        required=True,
        initial=400,
        help_text='TODO'
    )
    ocr_mode = forms.TypedChoiceField(
        choices=(
            ('auto', 'Auto'),
            ('on', 'On (force)'),
            ('off', 'Off'),
        ),
        initial="auto",
        label='OCR Mode:',
        coerce=str,
        help_text='TODO'
    )
    tesseract_language = forms.TypedChoiceField(
        choices=(
            ("eng", 'English'),
            ("deu", 'Deutsch'),
        ),
        initial="eng",
        label='Tesseract Language:',
        coerce=str,
        help_text='Choose the language, that tesseract should use to create the OCR.'
    )

    def get_hierarchy(self) -> dict:
        # deactivate child options if they are made irrelevant by a certain configuration
        return {
            "simple_and_lossless": {
                "type": "bool",
                "hide_state": "True",
                "children": [
                    "compression_mode",
                    "default_pdf_dpi",
                    "ocr_mode",
                    "tesseract_language"
                ]
            },
            "ocr_mode": {
                "type": "choice",
                "values_for_deactivation": ["off"],
                "children": [
                    "tesseract_language"
                ]
            }
        }
        # TODO document/implement a combi type
        # TODO document/implement an option to have multiple hierarchies per field
