import os.path
from functools import reduce

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import UploadedFile


# Create your views here.
def render_main_view(request):
    uploaded_files = UploadedFile.objects.order_by('-date_of_upload')  # sorting useful?
    context = {
        'uploaded_files': uploaded_files,
        "default_language": "eng",
        "languages": [
            {"value": "eng", "text": "English"},
            {"value": "deu", "text": "Deutsch"}
        ]
    }
    return render(request, 'application/main.html', context)


def download_processed_file(request):
    queue_csrf_token = request.GET.get("queue_csrf_token")
    if request.method == 'GET' and queue_csrf_token is not None:
        # TODO model to get path of finished file from user_id and csrf_token combination
        #  maybe replace all input files with the result and return that as download_file_path
        download_file_path = "path"
        return JsonResponse({
            "status": 200,
            "download_file_path": download_file_path,
            "queue_csrf_token": queue_csrf_token
        }, status=200)
    return JsonResponse({"status": 405}, status=405)


def processing_of_queue_is_finished(request):
    """
        :param request.GET.queue_csrf_token - csrf_token that was used for the file upload
        :returns json.finished - boolean True if all files from 'queue_csrf_token' and current user_id are processed
    """
    if request.method == 'GET':
        queue_csrf_token = request.POST.get("queue_csrf_token")
        boolean_list_of_finished_for_current_queue = UploadedFile.objects.filter(
            user_id=request.session["user_id"],
            csrf_token=queue_csrf_token
        ).values_list('finished', flat=True)

        processing_of_files_is_finished = reduce(
            lambda prev_result, current: prev_result and current, boolean_list_of_finished_for_current_queue, True
        )

        return JsonResponse({
            "status": 200,
            "finished": processing_of_files_is_finished,
            "queue_csrf_token": queue_csrf_token
        }, status=200)
    return JsonResponse({"status": 405}, status=405)


def render_form_submit_view(request):
    if request.method == 'POST':
        # TODO POST value validating with django forms
        user_id = request.session['user_id']
        # first show all files from the last request, that can be downloaded
        # or if they are not ready, yet, show a wait thing
        # underneath show all files that can be downloaded for this user_id (in defined time span)

        uploaded_file = request.FILES.get('file')


        UploadedFile.objects.create(
            uploaded_file=uploaded_file,
            user_id=user_id,
            csrf_token=request.POST.get("csrfmiddlewaretoken")
        )
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
