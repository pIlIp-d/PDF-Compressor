import os
from django.core.exceptions import ValidationError


def validate_file_extension(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1]  # returns path+filename
    valid_extensions = ['pdf', 'png', 'jpg', 'jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError("File extension isn't supported.")
