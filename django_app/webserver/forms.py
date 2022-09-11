from django import forms


class PdfCompressorForm(forms.Form):
    merge_pdfs = forms.BooleanField(
        label='Merge files into a single PDF.',
        initial=False,
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
    force_ocr = forms.BooleanField(
        label='Text recognition (OCR):',
        initial=False,
        help_text="TODO"
    )
    no_ocr = forms.BooleanField(
        label='No Text recognition (OCR)',
        initial=False,
        help_text="TODO"
    )
    simple_and_lossless = forms.BooleanField(
        label='Simple and lossless:',
        initial=False,
        help_text="TODO"
    )
    tesseract_language = forms.TypedChoiceField(
        choices=(
            ("eng", 'English'),
            ("deu", 'Deutsch'),
        ),
        initial="eng",
        label='Compression mode:',
        coerce=str,
        help_text='Choose the language, that tesseract should use to create the OCR.'
    )
