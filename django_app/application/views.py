import os.path

from django.shortcuts import render, redirect

from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse

from pdfcompressor.pdfcompressor import PDFCompressor
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
    return HttpResponse("405 Method Not Allowed. Try using POST", status=405)


def render_download_files_view(request):
    return JsonResponse("TODO")


def render_form_submit_view(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        # first show all files from the last request, that can be downloaded
        # or if they are not ready, yet, show a wait thing
        # underneath show all files that can be downloaded for this user_id (in defined time span

        user_id = request.session["user_id"]
        uploaded_file = request.FILES.get('file')

        file_path = os.path.join(".", "media", "uploaded_files", f"user_{user_id}", uploaded_file.name)

        UploadedFile.create(uploaded_file=uploaded_file, user_id=user_id)

        print("file_path:", file_path)

        """
        data_query = request.POST
        PDFCompressor(
            file_path,
            data_query.destination_path,
            data_query.compression_mode,
            data_query.force_ocr,
            data_query.no_ocr,
            True,
            data_query.tesseract_language,
            data_query.simple_and_lossless,
            data_query.default_pdf_dpi
        ).compress()
        """

        return HttpResponse('upload')
    return HttpResponse("405 Method Not Allowed. Try using POST", status=405)
