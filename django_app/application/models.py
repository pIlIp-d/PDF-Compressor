import os.path
from django.db import models


def get_directory_to_save_file_in(instance, filename: str) -> str:
    """
        :return example i.e: 'images/user_af2098.../filename.xxx'
    """
    path = os.path.join("uploaded_files", f"user_{instance.user_id}", filename)

    # already a file with the same name
    if os.path.isfile(os.path.join(".", "media", path)):
        pass  # maybe reformat the filename of duplicates

    return path


class UploadedFile(models.Model):
    filename = models.TextField()
    user_id = None
    uploaded_file = models.ImageField(upload_to=get_directory_to_save_file_in)
    date_of_upload = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, uploaded_file, user_id: str):
        cls.user_id = user_id
        cls.objects.create(uploaded_file=uploaded_file)

    def __str__(self):
        return str(self.pk)


class Meta:
    verbose_name_plural = 'Uploaded files'
