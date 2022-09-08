import os.path
import subprocess
from functools import reduce

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_apscheduler.scheduler import Scheduler
from apscheduler.triggers.date import DateTrigger

from .forms import PdfCompressorForm
from .models import UploadedFile, get_directory_for_file
from django.conf import settings

FORCE_SILENT_PROCESSING = True

MEDIA_FOLDER_PATH = os.path.abspath(os.path.join(".", "media"))


# Create your views here.
def render_main_view(request):
    allowed_file_endings = [".pdf", ".png"]
    form = PdfCompressorForm()
    context = {
        "dir": "/",
        "allowed_file_endings": allowed_file_endings,
        "form": form
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


def compress_pdf(source_path, destination_path, mode, force_ocr, no_ocr, tesseract_language, simple_and_lossless, dpi):
    options = [
        "python3", "../__main__.py",
        "-p", os.path.abspath(source_path),
        "-o", destination_path,
        "-m", str(mode),
        "-l", tesseract_language,
        "--dpi", str(dpi)
    ]
    if force_ocr:
        options.append("--force-ocr")
    if no_ocr:
        options.append("--no-ocr")
    if simple_and_lossless:
        options.append("--simple-and-lossless")
    if not settings.DEBUG or FORCE_SILENT_PROCESSING:
        options.append("--quiet")
    return_code = subprocess.call(options)
    if not return_code == 0:
        pass  # TODO some kind of error
    else:
        pass  # TODO alter finished field of uploaded files


def render_download_view(request):
    if request.method == 'POST':
        user_id = request.session["user_id"]
        queue_csrf_token = request.POST.get("csrfmiddlewaretoken")
        file_list = UploadedFile.objects.filter(
            user_id=user_id,
            csrf_token=queue_csrf_token
        )
        source_path = os.path.join(MEDIA_FOLDER_PATH,
                                   get_directory_for_file(user_id=user_id, csrf_token=queue_csrf_token))
        destination_path = request.POST.get("destination_file")
        if len(file_list) == 1:
            source_path = os.path.join(MEDIA_FOLDER_PATH, file_list[0].uploaded_file.name)
            if destination_path == "default":  # TODO destination path formatting check
                destination_path = source_path[:-4] + "_compressed.pdf"

        args = (
            source_path,
            destination_path,
            request.POST.get("compression_mode"),
            True if request.POST.get("force_ocr") == "on" else False,
            True if request.POST.get("no_ocr") == "on" else False,
            request.POST.get("tesseract_language"),
            True if request.POST.get("simple_and_lossless") == "on" else False,
            request.POST.get("default_pdf_dpi")
        )
        Scheduler.add_job(
            compress_pdf,
            trigger=DateTrigger(),
            replace_existing=False,
            args=args
        )

        return JsonResponse({"status": "200"}, status=200)
        # TODO POST value validating with django forms
        # TODO return the download page, where a timed function requests processing_of_queue_is_finished and
        #  afterwards activates button for download of result
    return JsonResponse({"status": 405, "error": "405 Method Not Allowed. Try using GET"}, status=405)


def upload_file(request):
    if request.method == 'POST':
        UploadedFile.objects.create(
            uploaded_file=request.FILES.get('file'),
            user_id=request.session['user_id'],
            csrf_token=request.POST.get("csrfmiddlewaretoken")
        )
        return HttpResponse('upload')
    return HttpResponse("405 Method Not Allowed. Try using POST", status=405)


def render_test_view(request):
    return HttpResponse("nothing here")