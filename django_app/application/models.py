import os.path
from django.db import models
from .validators import validate_file_extension


def get_directory_to_save_file_in(instance, filename: str) -> str:
    path = os.path.join("uploaded_files", f"user_{instance.user_id}", filename)
    if os.path.isfile(os.path.join(".", "media", path)):  # already a file with the same name
        pass  # maybe reformat the filename of duplicates

    return path


class UploadedFile(models.Model):
    filename = models.TextField()
    user_id = models.CharField(max_length=64)
    finished = models.BooleanField(default=False)
    uploaded_file = models.ImageField(upload_to=get_directory_to_save_file_in,
                                      validators=[validate_file_extension])
    # allowed extensions['pdf','png','jpg','jpeg']
    date_of_upload = models.DateTimeField(auto_now_add=True)
    csrf_token = models.CharField(max_length=32)

    def __str__(self):
        return str(self.pk)  # returns the primary key


class Meta:
    verbose_name_plural = 'Uploaded files'
