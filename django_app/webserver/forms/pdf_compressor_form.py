from django import forms


class PdfCompressorForm(forms.Form):
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
