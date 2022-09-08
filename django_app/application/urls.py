from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'application'

rest_api_urlspatterns = [
    path('processing_of_queue_is_finished/', views.processing_of_queue_is_finished, name='processing-of-queue-is-finished'),
    path('download_processed_file/', views.download_processed_file, name='download-processed-file'),
    path('uploads_finished/', views.uploads_finished, name='uploads-finished'),
    path('upload_file/', views.upload_file, name='upload-file'),

]

urlpatterns = [
    path('', views.render_main_view, name='main-view'),
    path('pdf-compressor/', views.render_main_view, name='main-view'),
    path('api/', include(rest_api_urlspatterns)),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
