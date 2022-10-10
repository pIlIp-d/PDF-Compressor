from django.contrib import admin

from django_app.webserver.models.uploaded_file import UploadedFile

# Register your models here.

admin.site.register(UploadedFile)
# TODO register the other models
