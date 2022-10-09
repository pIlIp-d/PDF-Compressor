from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import main_view, download_view
from ..api.urls import urlpatterns as api_urls
from . import views

app_name = 'webserver'

urlpatterns = [
    path('', main_view.render_main_view, name='main-view'),
    path('download/', download_view.render_download_view, name='download_view'),
    path('start_processing_and_show_download_view/', download_view.start_processing_and_show_download_view,
         name='start_processing_and_show_download_view'),
    path('api/', include(api_urls))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
