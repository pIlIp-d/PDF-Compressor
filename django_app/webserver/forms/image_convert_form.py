from django import forms

allowed_file_endings = [".png", ".jpeg", ".jpg"]  # no ',' allowed in file ending


class ImageConvertForm(forms.Form):
    result_file_types = forms.TypedChoiceField(
        choices=(
            (i, ending) for i, ending in zip(range(len(allowed_file_endings)), allowed_file_endings)
        ),
        label='Convert to:',
        coerce=str,
        help_text='TODO'
    )
