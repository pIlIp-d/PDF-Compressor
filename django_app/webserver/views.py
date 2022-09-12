import os.path
from functools import reduce

from apscheduler.triggers.date import DateTrigger
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from rest_apscheduler.scheduler import Scheduler

from pdfcompressor.pdfcompressor import PDFCompressor
from .forms import PdfCompressorForm
from .models import UploadedFile, get_or_create_new_request, \
    get_request_id, get_file_list_of_current_request, MEDIA_FOLDER_PATH, get_all_processing_files, ProcessedFile
from .custom_models.path_parser import PathParser
from .custom_models.process_stats_event_handler import ProcessStatsEventHandler

FORCE_SILENT_PROCESSING = False


# Create your views here.
def render_main_view(request):
    allowed_file_endings = [".pdf", ".png"]
    form = PdfCompressorForm()
    context = {
        "dir": "/",
        "allowed_file_endings": allowed_file_endings,
        "form": form,
        "user_id": request.session["user_id"],
    }
    return render(request, 'application/main.html', context)


def render_download_view(request):
    # save queue_csrf_token from used method or leave it empty
    queue_csrf_token = request.GET.get("csrfmiddlewaretoken") or request.POST.get("csrfmiddlewaretoken") or ""
    if not (request.method == "POST" or request.method == "GET"):
        return wrong_method_error("GET", "POST")

    user_id = request.session["user_id"]
    request_id = get_request_id(user_id, queue_csrf_token)

    context = {
        "request_id": request_id,
        "dir": "../",
        "user_id": request.session["user_id"],
        "queue_csrf_token": queue_csrf_token,
        "processing_files": get_all_processing_files(user_id)
    }
    return render(request, 'application/download.html', context)


def get_download_path_of_processed_file(request):
    queue_csrf_token = request.GET.get("queue_csrf_token")
    if request.method == 'GET' and queue_csrf_token is not None:
        download_file_path = "path"
        # TODO get file path
        return JsonResponse({
            "status": 200,
            "download_file_path": download_file_path
        }, status=200)
    return wrong_method_error("GET")


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

    return wrong_method_error("GET")


def wrong_method_error(*allowed_methods):
    method_hint = "".join("Try using " if i == 1 else "or" + allowed_methods[i] for i in range(len(allowed_methods)))
    return JsonResponse({"status": 405, "error": "Method Not Allowed. " + method_hint}, status=405)


# TODO /api/rename_file


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
        processing_request = get_or_create_new_request(
            request.session["user_id"],
            request.POST.get("csrfmiddlewaretoken"),
            "compressed"
        )
        if processing_request.finished:
            return JsonResponse({"status": 429, "error": "You already send this request."}, status=429)
        file_list = get_file_list_of_current_request(processing_request.id)
        if len(file_list) < 1:
            return JsonResponse({"status": 412, "error": "No files were found for this request."}, status=412)

        processed_files_list = []
        path_parser = PathParser(file_list[0].uploaded_file.name, processing_request.id, processing_request.path_extra)

        # add zip-file path
        processed_zip_file = ProcessedFile.add_processed_file_by_id("", processing_request.id)
        current_time = processed_zip_file.date_of_upload
        # override processed_file_path
        processed_zip_file.processed_file_path = path_parser.get_zip_destination_path(current_time)
        processed_zip_file.save()

        if request.POST.get("merge_pdfs") == "on":
            # add merge pdf-file path
            processed_file = ProcessedFile.add_processed_file_by_id(
                path_parser.get_merged_destination_path(current_time),
                processing_request.id
            )
            processed_files_list.append(processed_file)
        else:
            # add all results
            for file in file_list:
                processed_file = ProcessedFile.add_processed_file_by_id(
                    path_parser.get_destination_path(file.uploaded_file.name),
                    processing_request.id
                )
                processed_file.save()
                processed_files_list.append(processed_file)

        stats = list()
        stats.append(ProcessStatsEventHandler(len(file_list), processed_files_list, processing_request))

        pdf_compressor = PDFCompressor(
            source_path=os.path.join(MEDIA_FOLDER_PATH, path_parser.get_source_dir()),
            destination_path="default",
            compression_mode=int(request.POST.get("compression_mode")),
            force_ocr=True if request.POST.get("force_ocr") == "on" else False,
            no_ocr=True if request.POST.get("no_ocr") == "on" else False,
            quiet=not settings.DEBUG or FORCE_SILENT_PROCESSING,
            tesseract_language=request.POST.get("tesseract_language"),
            simple_and_lossless=True if request.POST.get("simple_and_lossless") == "on" else False,
            default_pdf_dpi=int(request.POST.get("default_pdf_dpi")),
            event_handler=stats
        )
        # start compression (async)
        Scheduler.add_job(
            pdf_compressor.compress,
            trigger=DateTrigger(),
            replace_existing=False
        )
    else:
        return wrong_method_error("POST")
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
