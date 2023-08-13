from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('upload_file/', views.upload_file, name='upload-file'),
    path('file/<int:file_id>/', views.remove_file, name='remove-file'),
    path('get_all_files/', views.get_all_files),
    path('get_all_files_of_request/', views.get_all_files_of_request),
    path('get_possible_destination_file_types/', views.get_possible_destination_file_types),
    path('get_allowed_input_file_types/', views.get_allowed_input_file_types),
    path('get_all_files_request_ids/', views.get_all_files_request_ids),
    path('get_possible_destination_file_types/<int:file_id>/', views.get_possible_destination_file_types_by_file_id),

    path('get_form_html_for_web_view/', views.get_form_html_for_web_view),

    path('finished_all_files/', views.finished_all_files),
    path('started_processing/', views.started_processing),

    path('get_csrf/', views.get_csrf),
    path('ping/', views.ping),

]
