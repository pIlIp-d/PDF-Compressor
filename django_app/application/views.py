import os.path

from django.shortcuts import render

from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse

from .models import UploadedFile


# Create your views here.
def render_main_view(request):
    uploaded_files = UploadedFile.objects.order_by('-date_of_upload')
    context = {
        'uploaded_files': uploaded_files,
        "default_language": "eng",
        "languages": [
            {
                "value": "eng",
                "text": "English"
            },
            {
                "value": "deu",
                "text": "Deutsch"
            }
        ]
    }
    return render(request, 'application/main.html', context)


def render_upload_view(request):
    if request.method == 'POST':
        current_file = request.FILES.get('file')
        user_id = request.session['user_id']
        UploadedFile.create(uploaded_file=current_file, user_id=user_id)
        return HttpResponse('upload')
    return JsonResponse({'post': 'false'})


def render_form_submit_view(request):
    # TODO convert to POST
    if request.method == 'GET' and request.GET["submit"] == "Compress":
        user_id = request.session['user_id']
        # first show all files from the last request, that can be downloaded
        # or if they are not ready, yet, show a wait thing
        # underneath show all files that can be downloaded for this user_id (in defined time span
        #
        data_query = request.GET
        user_id = request.session["user_id"]
        file_folder_path = os.path.join(".", "media", "uploaded_files", f"user_{user_id}")

        pass
    return JsonResponse(request.GET)
