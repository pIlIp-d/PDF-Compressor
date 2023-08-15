from django import forms

from plugin_system.plugin_form import PluginForm


class PdfCompressorForm(PluginForm):
    merge_files = forms.BooleanField(
        label='Merge files into a single PDF.',
        initial=False
    )
    simple_and_lossless = forms.BooleanField(
        label='Simple and lossless:',
        initial=True,
        help_text="Is much faster. It's optimal if your pdf is just typed text. If you compress a handwriting or "
                  "photo-scan you get much better results deactivating this option."
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
    )
    default_pdf_dpi = forms.IntegerField(
        label='Default DPI:',
        min_value=10,
        max_value=1000,
        step_size=10,
        required=True,
        initial=350,
        help_text='Smaller numbers improve compression, higher numbers can have better '
                  'quality. For handwriting about 200-300 is enough.'
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

    def get_advanced_options(self) -> list[str]:
        return ["compression_mode", "merge_files", "ocr_mode", "simple_and_lossless", "default_pdf_dpi",
                "simple_and_lossless", "tesseract_language"]


class GoodNotesCompressorForm(PdfCompressorForm):
    def __init__(self):
        super().__init__()
        self.fields['simple_and_lossless'].initial = False
        self.fields['compression_mode'].initial = 1
        self.fields['default_pdf_dpi'].initial = 200


class PngCompressorForm(PluginForm):
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


class ImageToPdfConvertForm(PluginForm):
    """
    merge_files = forms.BooleanField(
        label='Merge files into a single PDF.',
        initial=False
    )
    """
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
        help_text='Choose the language, that tesseract should use to create the OCR(Optical Character Recognition).'
    )

    def get_hierarchy(self) -> dict:
        return {
            "ocr_mode": {
                "type": "choice",
                "values_for_deactivation": ["off"],
                "children": [
                    "tesseract_language"
                ]
            }
        }


class PdfToImageConvertForm(PluginForm):
    default_pdf_dpi = forms.IntegerField(
        label='Default DPI:',
        min_value=10,
        max_value=1000,
        step_size=10,
        required=True,
        initial=350,
        help_text='Smaller numbers improve compression, higher numbers can have better '
                  'quality. For handwriting about 200-300 is enough.'
    )
