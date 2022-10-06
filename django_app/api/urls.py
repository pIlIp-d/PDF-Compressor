from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('upload_file/', views.upload_file, name='upload-file'),
    path('remove_file/', views.remove_file, name='remove-file'),
    path('started_request_processing/', views.started_request_processing, name='started_request_processing'),
    path('finish_file/', views.finish_file, name='finish-file'),
    path('finish_request/', views.finish_request, name='finish-request'),
    path('get_all_files/', views.get_all_files, name="get-all-files")
]
