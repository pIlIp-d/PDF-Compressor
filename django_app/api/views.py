from functools import reduce

from django.http import JsonResponse

from django_app.api.decorators import only_for_localhost
from django_app.webserver.models import UploadedFile, ProcessingFilesRequest, ProcessedFile


def get_download_path_of_processed_file(request):
    queue_csrf_token = request.GET.get("queue_csrf_token")
    if request.method == 'GET' and queue_csrf_token is not None:
        ProcessedFile.get_all_processing_files(request.session["user_id"])

        download_file_path = "path"
        # TODO get file path
        return JsonResponse({
            "status": 200,
            "download_file_path": download_file_path
        }, status=200)
    return wrong_method_error("GET")


def get_all_files(request):
    if request.method == "GET":
        files_json = ProcessedFile.get_all_processing_files(request.session["user_id"])
        return JsonResponse({"status": 200, "files": files_json}, status=200)
    return wrong_method_error("GET")


def processing_of_queue_is_finished(request):
    """
        :param request.GET.queue_csrf_token - csrf_token that was used for the file upload
        :returns json.Finished - boolean True if all files from 'queue_csrf_token' and current user_id are processed
    """
    if request.method == 'GET':
        queue_csrf_token = request.POST.get("queue_csrf_token")
        boolean_list_of_finished_for_current_queue = ProcessingFilesRequest.get_uploaded_file_list_of_current_request(
            ProcessingFilesRequest.get_request_id(
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


def parameter_missing_error(parameter_name: str):
    return JsonResponse({"status": 400, "error": f"Parameter '{parameter_name}' is required!"}, status=412)


# TODO /api/rename_file

def remove_file(request):
    if request.method == "GET":
        file = None
        if request.GET.get("file_origin") == "uploaded":
            file = UploadedFile.objects.filter(
                id=request.GET.get("file_id")
            ).first()
        elif request.GET.get("file_origin") == "processed":
            file = ProcessedFile.objects.filter(
                id=request.GET.get("file_id")
            ).first()

        print(file)
        if file is not None and file.processing_request.user_id == request.session["user_id"]:
            file.delete()
        else:
            return JsonResponse({"status": 412, "error": "No file with that id found for you."}, status=412)
        return JsonResponse({"status": 200, "error": "Removed file successfully."}, status=200)
    return wrong_method_error("GET")


def upload_file(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        csrfmiddlewaretoken = request.POST.get("csrfmiddlewaretoken")
        uploaded_file = UploadedFile(
            uploaded_file=request.FILES.get('file'),
            processing_request=ProcessingFilesRequest.get_or_create_new_request(user_id, csrfmiddlewaretoken),
            valid_file_endings=".pdf"
        )
        uploaded_file.save()
        file_id = uploaded_file.id
        return JsonResponse({"file_id": file_id})
    return wrong_method_error("POST")


@only_for_localhost
def finish_file(request):
    if request.method == "GET":
        if "processed_file_path" in request.GET:
            file = ProcessedFile.objects.filter(processed_file_path=request.GET.get("processed_file_path"))
            file.finished = True
            file.save()
            return JsonResponse({"status": 200}, status=200)
        else:
            return parameter_missing_error("processed_file_path")
    else:
        return wrong_method_error("GET")


@only_for_localhost
def finish_request(request):
    if request.method == "GET":
        if "request_id" in request.GET:
            processing_request = ProcessingFilesRequest.get_request_by_id(request.GET.get("request_id"))
            for file in ProcessedFile.objects.filter(processing_request=processing_request):
                file.finished = True
                file.save()
            processing_request.finished = True
            processing_request.save()
            return JsonResponse({"status": 200}, status=200)
        else:
            return parameter_missing_error("request_id")
    else:
        return wrong_method_error("GET")


@only_for_localhost
def started_request_processing(request):
    if request.method == "GET":
        if "request_id" in request.GET:
            print(request.GET.get("request_id"))
            processing_request = ProcessingFilesRequest.get_request_by_id(request.GET.get("request_id"))
            processing_request.started = True
            processing_request.save()
            return JsonResponse({"status": 200}, status=200)
        else:
            return parameter_missing_error("request_id")
    else:
        return wrong_method_error("GET")
