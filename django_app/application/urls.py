from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'application'

urlpatterns = [
    path('', views.render_main_view, name='main-view'),
    path('pdf-compressor/', views.render_main_view, name='main-view'),
    path('upload/', views.render_upload_view, name='upload-view'),
    path('form_submit/', views.render_form_submit_view, name='form-submit-view'),
    # path('download_files/', views.render_download_files_view, name='download-files-view'),
    # path('download_files/', views.render_download_files_view, name='download-files-view'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
