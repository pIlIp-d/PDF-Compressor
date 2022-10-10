from functools import reduce

from django.http import JsonResponse
from django.shortcuts import render, redirect

from django_app.api.views import wrong_method_error
from django_app.webserver.models import ProcessingFilesRequest, ProcessedFile
from plugins.pdfcompressor.plugin_config import Plugin

FORCE_SILENT_PROCESSING = False


def get_directory_for_html(request) -> str:
    return reduce(
        lambda dir_string, _: ".." + dir_string,
        range(len(request.META['PATH_INFO'].split("/")) - 2),
        "/"
    )


def render_main_view(request):
    context = {
        "dir": get_directory_for_html(request),
        "user_id": request.session["user_id"],
        "request_id": request.session["request_id"]
    }
    return render(request, 'application/main.html', context)


def render_download_view(request):
    if not (request.method == "POST" or request.method == "GET"):
        return wrong_method_error("GET", "POST")
    context = {"dir": "../"}
    return render(request, 'application/download.html', context)


def start_processing_and_show_download_view(request):
    if request.method == 'POST':
        processing_request = ProcessingFilesRequest.get_or_create_new_request(
            request.session["user_id"],
            request.POST.get("request_id"),
        )
        destination_type_select = request.POST.get("destination_type_select")
        plugin = Plugin.get_processing_plugin_by_name(destination_type_select.split(":")[0])
        destination_file_ending = Plugin.COMPRESSION_TYPE if destination_type_select.split(": ")[1] else \
            destination_type_select.split(": ")[1]

        processing_request.path_extra = request.POST.get("processing_file_extension")
        processing_request.save()

        if processing_request.finished or processing_request.started:
            return JsonResponse({"status": 429, "error": "You already send this request."}, status=429)

        input_file_list = ProcessingFilesRequest.get_uploaded_file_list_of_current_request(processing_request)
        if len(input_file_list) < 1:
            return JsonResponse({"status": 412, "error": "No files were found for this request."}, status=412)

        # add zip-file path
        zip_file = ProcessedFile.add_processed_file("", processing_request)
        current_time = zip_file.date_of_upload

        # override processed_file_path
        zip_file.processed_file_path = processing_request.get_merged_destination_path(current_time, ".zip")
        zip_file.save()

        processed_files_list = [zip_file]
        if request.POST.get("merge_files") == "on":
            # add merge pdf-file path
            processed_file = ProcessedFile.add_processed_file(
                processing_request.get_merged_destination_path(
                    zip_file.date_of_upload,
                    destination_file_ending
                ),
                processing_request
            )
            processed_files_list.append(processed_file)
        else:
            # add all results
            for file in input_file_list:
                processed_file = ProcessedFile.add_processed_file(
                    processing_request.get_destination_path(file.uploaded_file.name),
                    processing_request
                )
                processed_file.save()
                processed_files_list.append(processed_file)

        plugin.get_task()(
            request_parameters=request.POST,
            processing_request=processing_request,
            processed_file_paths=[file.processed_file_path for file in processed_files_list]
        ).create()
    else:
        return wrong_method_error("POST")
    return redirect("../download/")
