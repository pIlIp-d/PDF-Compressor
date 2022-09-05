from django.views.generic import TemplateView


# Create your views here.

class MainView(TemplateView):
    template_name = 'PDF-Compressor/App/Templates/main.html'
