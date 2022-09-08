import os
import os.path
import pathlib
from django.db import models
from jsons import ValidationError
from natsort import natsorted


#  Depending on the attributes of the file gets stored in a different directory
def get_directory_to_save_file_in(instance, filename: str) -> str:

    path = os.path.join("uploaded_files", f"user{instance.user_id}", filename)
    if os.path.isfile(os.path.join(".", "media", path)):
        os.chdir(path)
        for current_file in sorted(os.listdir(path)):  # rename
            print(current_file)

    extension_of_file = pathlib.Path(path).suffixes[-1].lower()
    if extension_of_file != '.pdf':
        raise ValidationError("Invalid extension. Only PDF-File's are allowed.")

    file_size = instance.uploaded_file.size
    if file_size > UploadedFile.MAX_FILESIZE:
        raise ValidationError("The maximum file size is reached.")

    return path


class UploadedFile(models.Model):
    MAX_FILESIZE = 10000000  # Bytes
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    uploaded_file = models.ImageField(upload_to=get_directory_to_save_file_in)
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)


def __str__(self):
    return str(self.pk)  # returns the primary key


class Meta:
    def __init__(self):
        pass

    verbose_name_plural = 'Uploaded files'
