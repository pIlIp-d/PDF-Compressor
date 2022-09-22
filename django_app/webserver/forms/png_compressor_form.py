from django import forms


class PngCompressorForm(forms.Form):
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
