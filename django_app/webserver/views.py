import os.path
from functools import reduce

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_apscheduler.scheduler import Scheduler
from apscheduler.triggers.date import DateTrigger

from . import models
from .forms import PdfCompressorForm
from .models import UploadedFile, get_directory_for_file
from django.conf import settings

FORCE_SILENT_PROCESSING = False



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


def render_download_view(request):
    # save queue_csrf_token from used method or leave it empty
    queue_csrf_token = request.GET.get("csrfmiddlewaretoken") or request.POST.get("csrfmiddlewaretoken") or ""
    if not (request.method == "POST" or request.method == "GET"):
        return wrong_method_error("GET", "POST")

    request_id = models.get_request_id(request.session["user_id"], queue_csrf_token)

    context = {
        "request_id": id,
        "dir": "/",
        "user_id": request.session["user_id"],
        "queue_csrf_token": queue_csrf_token
    }
    return render(request, 'application/download.html', context)


def get_download_path_of_processed_file(request):
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
        boolean_list_of_finished_for_current_queue = get_file_list_of_current_request(
            get_request_id(
                user_id=request.session["user_id"],
                queue_csrf_token=queue_csrf_token
            )
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
    return len([name for name in os.listdir('../../application') if os.path.isfile(dir_name)])



def remove_file(request):
    if request.method == "GET":
        uploaded_file = UploadedFile.objects.filter(
            id=request.GET.get("file_id")
        )
        print(uploaded_file)
        if len(uploaded_file) == 1 and uploaded_file[0].processing_request.user_id == request.session["user_id"]:
            uploaded_file[0].uploaded_file.delete()
            uploaded_file[0].delete()
        else:
            return JsonResponse({"status": 412, "error": "No file with that id found."}, status=412)
        return JsonResponse({"status": 200, "error": "Removed file successfully."}, status=200)
    return wrong_method_error("GET")


# TODO POST value validating with django forms

def start_pdf_compression_and_show_download_view(request):
    if request.method == 'POST':
        user_id = request.session["user_id"]
        queue_csrf_token = request.POST.get("csrfmiddlewaretoken")
        get_or_create_new_request(user_id, queue_csrf_token)

        request_id = get_request_id(user_id, queue_csrf_token)

        file_list = get_file_list_of_current_request(request_id)

        if len(file_list) < 1:
            return JsonResponse({"status": 412, "error": "No files were found for this request."}, status=412)

        source_path = os.path.join(MEDIA_FOLDER_PATH, os.path.dirname(file_list[0].uploaded_file.name))

        merge_pdfs = True if request.POST.get("merge_pdfs") == "on" else False

        destination_path = "default"
        if merge_pdfs:
            destination_path = os.path.join(os.path.dirname(source_path), "merged.pdf")

        print(source_path, destination_path)

        stats = list()
        stats.append(ProcessStatsProcessor(len(file_list)))

        pdf_compressor = PDFCompressor(
            source_path=source_path,
            destination_path=destination_path,
            compression_mode=int(request.POST.get("compression_mode")),
            force_ocr=True if request.POST.get("force_ocr") == "on" else False,
            no_ocr=True if request.POST.get("no_ocr") == "on" else False,
            quiet=not settings.DEBUG or FORCE_SILENT_PROCESSING,
            tesseract_language=request.POST.get("tesseract_language"),
            simple_and_lossless=True if request.POST.get("simple_and_lossless") == "on" else False,
            default_pdf_dpi=int(request.POST.get("default_pdf_dpi")),
            extra_preprocessors=stats,
            extra_postprocessors=stats
        )
        # update db
        start_process(request_id)
        # start compression (async)
        Scheduler.add_job(
            pdf_compressor.compress,
            trigger=DateTrigger(),
            replace_existing=False
        )
    elif request.method == "GET":
        queue_csrf_token = request.GET.get("csrfmiddlewaretoken") or ""
    return redirect("../download/")


def upload_file(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        csrfmiddlewaretoken = request.POST.get("csrfmiddlewaretoken")
        uploaded_file = UploadedFile(
            uploaded_file=request.FILES.get('file'),
            processing_request=get_or_create_new_request(user_id, csrfmiddlewaretoken),
            valid_file_endings=".pdf"
        )
        uploaded_file.save()
        file_id = uploaded_file.id
        return JsonResponse({"file_id": file_id})
    return wrong_method_error("POST")


def render_test_view(request):
    return HttpResponse("nothing here")
