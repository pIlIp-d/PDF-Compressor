from functools import reduce

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from django_app.api.decorators import only_for_localhost
from django_app.webserver.models import UploadedFile, ProcessingFilesRequest, ProcessedFile
from django_app.webserver.validators import get_file_extension

# TODO favicon.ico
# TODO move valid_file_endings from UploadedFile -> request Table


@csrf_protect
def get_all_files(request):
    if request.method == "GET":
        files_json = ProcessedFile.get_all_processing_files(request.session["user_id"])
        return JsonResponse({"status": 200, "files": files_json}, status=200)
    return wrong_method_error("GET")


def wrong_method_error(*allowed_methods):
    method_hint = "".join("Try using " if i == 1 else "or" + allowed_methods[i] for i in range(len(allowed_methods)))
    return JsonResponse({"status": 405, "error": "Method Not Allowed. " + method_hint}, status=405)


def parameter_missing_error(parameter_name: str):
    return JsonResponse({"status": 400, "error": f"Parameter '{parameter_name}' is required!"}, status=412)


# TODO /api/rename_file

@csrf_protect  # TODO csrf_protect doesn't work, yet
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
        else:
            return JsonResponse({"status": 412, "error": "Parameter file_origin is required."}, status=412)

        print(file)
        if file is not None and file.processing_request.user_id == request.session["user_id"]:
            file.delete()
        else:
            return JsonResponse({"status": 412, "error": "No file with that id found for you."}, status=412)
        return JsonResponse({"status": 200, "error": "Removed file successfully."}, status=200)
    return wrong_method_error("GET")


@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        csrfmiddlewaretoken = request.POST.get("csrfmiddlewaretoken")
        uploaded_file = UploadedFile(
            uploaded_file=request.FILES.get('file'),
            processing_request=ProcessingFilesRequest.get_or_create_new_request(user_id, csrfmiddlewaretoken),
            valid_file_endings=get_file_extension(request.FILES.get('file').name)
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
