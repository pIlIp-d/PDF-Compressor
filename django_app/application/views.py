from django.shortcuts import render

from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse

from .models import UploadedFile


# Create your views here.
def render_main_view(request):
    uploaded_files = UploadedFile.objects.order_by('-date_of_upload')
    context = {'uploaded_files': uploaded_files}
    return render(request, 'application/main.html', context)


def render_upload_view(request):
    if request.method == 'POST':
        current_file = request.FILES.get('file')
        user_id = request.session['user_id']
        UploadedFile.create(uploaded_file=current_file, user_id=user_id)
        return HttpResponse('upload')
    return JsonResponse({'post': 'false'})


def render_form_submit_view(request):
    return JsonResponse({'implemented': 'false'})
