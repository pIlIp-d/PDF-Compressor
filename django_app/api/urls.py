from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('processing_of_queue_is_finished/', views.processing_of_queue_is_finished,
         name='processing-of-queue-is-finished'),
    path('get_download_path_of_processed_file/', views.get_download_path_of_processed_file,
         name='get-download-path-of-processed-file'),
    path('upload_file/', views.upload_file, name='upload-file'),
    path('remove_file/', views.remove_file, name='remove-file'),
]