from functools import reduce

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from django_app.plugin_system.plugin import Plugin
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.models.uploaded_file import UploadedFile

FORCE_SILENT_PROCESSING = False


def get_directory_for_html(request) -> str:
    return reduce(
        lambda dir_string, _: ".." + dir_string,
        range(len(request.META['PATH_INFO'].split("/")) - 2),
        "/"
    )


@require_http_methods(["GET"])
def render_main_view(request):
    context = {
        "dir": get_directory_for_html(request),
        "user_id": request.session["user_id"],  # TODO necessary ?
        "request_id": request.session["request_id"],
        "plugin": request.GET.get("plugin") or "null"
    }
    return render(request, 'application/main.html', context)


@require_http_methods(["GET"])
def render_download_view(request):
    context = {"dir": get_directory_for_html(request)}
    return render(request, 'application/download.html', context)


@require_http_methods(["POST"])
def start_processing_and_show_download_view(request):
    processing_request = ProcessingFilesRequest.get_or_create_new_request(
        request.session["user_id"],
        request.POST.get("request_id"),
    )
    destination_type_select = request.POST.get("destination_type_select")
    plugin = Plugin.get_processing_plugin_by_name(destination_type_select.split(":")[0])
    if processing_request.finished or processing_request.started:
        return JsonResponse({"status": 429, "error": "You already send this request."}, status=429)

    input_file_list = UploadedFile.get_uploaded_file_list_of_current_request(processing_request)
    if len(input_file_list) < 1:
        return JsonResponse({"status": 412, "error": "No files were found for this request."}, status=412)

    plugin.get_task()(
        request_parameters=request.POST,
        processing_request=processing_request,
    ).create()
    return redirect("../download/")
