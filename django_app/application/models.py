from uuid import UUID

from django.db import models


# Create your models here.

def get_current_user_id():
    return "0000"


def get_directory_to_save_file_in(_, filename: str) -> str:
    """
        :return example i.e: 'images/user_af2098.../'
    """
    return f"images/user_{get_current_user_id()}/{filename}"


class UploadedFile(models.Model):
    filename = models.TextField()
    uploaded_file = models.ImageField(upload_to=get_directory_to_save_file_in)
    date_of_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)


class Meta:
    verbose_name_plural = 'Uploaded files'
