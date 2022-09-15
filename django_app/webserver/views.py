from apscheduler.triggers.date import DateTrigger
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from rest_apscheduler.scheduler import Scheduler

from pdfcompressor.pdfcompressor import PDFCompressor
from pdfcompressor.utility.console_utility import ConsoleUtility
from .forms import PdfCompressorForm
from .models import ProcessedFile, ProcessingFilesRequest, get_local_relative_path
from .custom_models.process_stats_event_handler import ProcessStatsEventHandler
from ..api.views import wrong_method_error

FORCE_SILENT_PROCESSING = False


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
    request_id = ProcessingFilesRequest.get_request_id(user_id, queue_csrf_token)

    context = {
        "request_id": request_id,
        "dir": "../",
        "user_id": request.session["user_id"],
        "queue_csrf_token": queue_csrf_token,
        "processing_files": ProcessedFile.get_all_processing_files(user_id)
    }
    return render(request, 'application/download.html', context)


# TODO POST value validating with django forms

def start_pdf_compression_and_show_download_view(request):
    if request.method == 'POST':
        processing_request = ProcessingFilesRequest.get_or_create_new_request(
            request.session["user_id"],
            request.POST.get("csrfmiddlewaretoken"),
            request.POST.get("processing_file_extension")
        )

        if processing_request.finished:
            return JsonResponse({"status": 429, "error": "You already send this request."}, status=429)
        file_list = ProcessingFilesRequest.get_file_list_of_current_request(processing_request.id)
        if len(file_list) < 1:
            return JsonResponse({"status": 412, "error": "No files were found for this request."}, status=412)

        processed_files_list = []

        # add zip-file path
        processed_zip_file = ProcessedFile.add_processed_file_by_id("", processing_request.id)
        current_time = processed_zip_file.date_of_upload
        # override processed_file_path
        processed_zip_file.processed_file_path = processing_request.get_zip_destination_path(current_time)
        processed_zip_file.save()

        destination_path = get_local_relative_path(processing_request.get_destination_dir())
        if request.POST.get("merge_pdfs") == "on":
            # add merge pdf-file path
            processed_file = ProcessedFile.add_processed_file_by_id(
                processing_request.get_merged_destination_path(current_time, ".pdf"),
                processing_request.id
            )
            processed_files_list.append(processed_file)
            # change destination path to get merged result
            destination_path = get_local_relative_path(processed_file.processed_file_path)
        else:
            # add all results
            for file in file_list:
                processed_file = ProcessedFile.add_processed_file_by_id(
                    processing_request.get_destination_path(file.uploaded_file.name),
                    processing_request.id
                )
                processed_file.save()
                processed_files_list.append(processed_file)

        stats = list()
        stats.append(ProcessStatsEventHandler(len(file_list), processed_files_list, processing_request))

        ConsoleUtility.print_error(destination_path)
        pdf_compressor = PDFCompressor(
            source_path=get_local_relative_path(processing_request.get_source_dir()),
            destination_path=destination_path,
            compression_mode=int(request.POST.get("compression_mode")),
            force_ocr=True if request.POST.get("ocr_mode") == "on" else False,
            no_ocr=True if request.POST.get("ocr_mode") == "off" else False,
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


def render_test_view(request):
    p = ProcessingFilesRequest.get_or_create_new_request(request.session["user_id"], "abc", "path_extra")
    print(p.get_local_relative_path(p.get_source_dir()))
    return HttpResponse("nothing here")
