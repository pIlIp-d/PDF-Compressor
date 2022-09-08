import os.path
from functools import reduce

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import UploadedFile


# Create your views here.
def render_main_view(request):
    uploaded_files = UploadedFile.objects.order_by('-date_of_upload')  # sorting useful?
    allowed_file_endings = [".pdf", ".png"]
    context = {
        'uploaded_files': uploaded_files,
        "default_language": "eng",
        "languages": [
            {"value": "eng", "text": "English"},
            {"value": "deu", "text": "Deutsch"}
        ],
        "allowed_file_endings": allowed_file_endings,
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
    return JsonResponse({"status": 405, "error": "405 Method Not Allowed. Try using GET"}, status=405)


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

    return JsonResponse({"status": 405, "error": "405 Method Not Allowed. Try using GET"}, status=405)


def _get_file_amount_in_directory(dir_name: str) -> int:
    return len([name for name in os.listdir('.') if os.path.isfile(dir_name)])


def uploads_finished(request):
    if request.method == 'POST':
        queue_csrf_token = request.POST.get("csrfmiddlewaretoken")
        print(request.post)
        # TODO run PDFCompressor async
        return JsonResponse({"status": 200}, status=200)
    return JsonResponse({"status": 405, "error": "405 Method Not Allowed. Try using POST"}, status=405)


def upload_file(request):
    if request.method == 'POST':
        # TODO POST value validating with django forms
        user_id = request.session['user_id']
        # first show all files from the last request, that can be downloaded
        # or if they are not ready, yet, show a wait thing
        # underneath show all files that can be downloaded for this user_id (in defined time span)

        uploaded_file = request.FILES.get('file')

        print(request.POST)

        csrfmiddlewaretoken = request.POST.get("csrfmiddlewaretoken")
        UploadedFile.objects.create(
            uploaded_file=uploaded_file,
            user_id=user_id,
            csrf_token=csrfmiddlewaretoken
        )
        return HttpResponse('upload')

    return HttpResponse("405 Method Not Allowed. Try using POST", status=405)

