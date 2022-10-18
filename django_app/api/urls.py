from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('upload_file/', views.upload_file, name='upload-file'),
    path('remove_file/', views.remove_file, name='remove-file'),
    path('get_all_files/', views.get_all_files, name="get-all-files"),
    path('get_possible_destination_file_types/', views.get_possible_destination_file_types),
    path('finished_all_files/', views.finished_all_files),
    path('started_processing/', views.started_processing),
    path('get_form_html_for_web_view/', views.get_form_html_for_web_view)
]
