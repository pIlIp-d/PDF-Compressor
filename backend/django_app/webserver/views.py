import datetime
import json
import os
import shutil
from functools import reduce
from glob import glob

from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from django_app import settings
from .decorators import requires_parameters
from plugin_system.plugin import Plugin
from ..settings import TIME_FORMAT, MEDIA_ROOT
from ..webserver.models.uploaded_file import UploadedFile
from ..webserver.validators import get_file_extension
from ..webserver.models.processed_file import ProcessedFile
from ..webserver.models.processing_files_request import ProcessingFilesRequest

from django.http import JsonResponse
from django.middleware.csrf import get_token
from ..celery import app as celery_app


def zip_file(source_folder, destination_file):
    filename_without_file_ending = ".".join(os.path.basename(destination_file).split(".")[:-1])
    # create zip-archive
    compression_format = "zip"
    shutil.make_archive(
        filename_without_file_ending,
        format=compression_format,
        root_dir=source_folder
    )
    # move file into final destination
    shutil.move(
        os.path.join(".", filename_without_file_ending + ".zip"),
        os.path.join(destination_file)
    )


def invalid_parameter_error(parameter_name: str):
    return JsonResponse({"status": 412, "error": f"Invalid value for parameter '{parameter_name}"}, status=412)


def internal_server_error(error_string: str):
    return JsonResponse({"status": 500, "error": error_string}, status=500)


def get_csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


def ping(request):
    return JsonResponse({'result': 'OK'})


def get_files_in_folder(folder_path: str):
    return glob(os.path.join(folder_path, "*"), include_hidden=True)


@csrf_protect
@require_http_methods(["GET"])
def get_all_files_request_ids(request):
    processing_requests = ProcessingFilesRequest.objects.filter(user_id=request.session.get("user_id"))
    return JsonResponse({"status": 200, "request_ids": [r.id for r in processing_requests]}, status=200)


@csrf_protect
@require_http_methods(["GET"])
def get_all_files(request):
    files_json = ProcessedFile.get_all_processing_files(request.session["user_id"])
    return JsonResponse({"status": 200, "files": files_json}, status=200)


def zip_result(processing_request):
    source_folder = os.path.join(
        MEDIA_ROOT, "uploaded_files", processing_request.user_id, str(processing_request.id)
    )
    shutil.rmtree(source_folder)
    destination_folder = source_folder + "_processed"
    zip_path = os.path.join(
        destination_folder, "processed_files_" + datetime.datetime.now().strftime(TIME_FORMAT) + ".zip"
    )
    # TODO replace with: if no folder exists throw an error
    os.makedirs(destination_folder, exist_ok=True)

    processed_files = get_files_in_folder(destination_folder)
    # if multiple files, compress them into a zip and use the zip instead
    if len(get_files_in_folder(destination_folder)) > 1:
        zip_file(destination_folder, zip_path)
        for f in processed_files:
            if os.path.isfile(f):
                os.remove(f)

    print("PROCESSED_FILES", get_files_in_folder(destination_folder))
    # add the resulting files in the processed dir to the db
    for file in reversed(get_files_in_folder(destination_folder)):
        def get_media_normalized_path(absolute_path):
            absolute_media_path = os.path.abspath(MEDIA_ROOT)
            if not absolute_path.startswith(absolute_media_path):
                raise ValueError("File is not inside the Media folder")
            return absolute_path[len(absolute_media_path) + 1:]

        ProcessedFile.add_processed_file(get_media_normalized_path(file), processing_request)
    processing_request.finished = True
    processing_request.save()


@csrf_protect
@require_http_methods(["GET"])
@requires_parameters("GET", ["request_id"])
def get_all_files_of_request(request):
    processing_request = ProcessingFilesRequest.objects.filter(
        id=request.GET.get("request_id"),
        user_id=request.session["user_id"])[0]
    celery_task = celery_app.AsyncResult(processing_request.celery_task_id)

    if celery_task.status == "SUCCESS" and not processing_request.finished:
        zip_result(processing_request)
    elif celery_task.status == "FAILURE":
        pass

    files_json = ProcessedFile.get_all_processing_files(request.session["user_id"], request.GET.get("request_id"))
    return JsonResponse({
        "status": 200,
        "files": files_json,
        "request_finished": celery_task.status == "SUCCESS"
    }, status=200)


@csrf_protect
@require_http_methods(["DELETE"])
@requires_parameters("GET", ["file_origin"])
def remove_file(request, file_id):
    if request.GET.get("file_origin") == "uploaded":
        file_class = UploadedFile
    elif request.GET.get("file_origin") == "processed":
        file_class = ProcessedFile
    else:
        return JsonResponse({"status": 412, "error": "Unknown value for file_origin."}, status=412)

    file = file_class.objects.filter(
        id=file_id
    ).first()

    if file is not None \
            and (not file.processing_request or file.processing_request.user_id == request.session["user_id"]):
        file.delete()
    else:
        return JsonResponse({"status": 412, "error": "No file with that id found for you."}, status=412)
    return JsonResponse({"status": 200, "success": "Removed file successfully."}, status=200)


@require_http_methods(["GET"])
@requires_parameters("GET", ["plugin_info"])
def get_allowed_input_file_types(request):
    plugin_info = request.GET.get("plugin_info")
    if plugin_info == "null":
        allowed_file_types = reduce(lambda allowed_types, plugin: allowed_types + plugin.get_input_file_types(),
                                    settings.PROCESSOR_PLUGINS, [])  # TODO reduce lists
    else:
        plugin_name = plugin_info.split(":")[0]
        plugin = Plugin.get_processing_plugin_by_name(plugin_name)  # check none
        allowed_file_types = plugin.get_input_file_types()  # TODO json

    return JsonResponse({"status": 200, "allowed_file_types": allowed_file_types}, status=200)


@csrf_protect
@require_http_methods(["POST"])
# @requires_parameters("POST", ["request_id"])
@requires_parameters("FILES", ["file"])
def upload_file(request):
    print(request.POST)
    print(request.FILES.get('file'))
    user_id = request.session['user_id']
    uploaded_file = UploadedFile(
        uploaded_file=request.FILES.get('file'),
        user_id=user_id,
        #        processing_request=ProcessingFilesRequest.get_or_create_new_request(user_id, request_id),
        valid_file_endings=get_file_extension(request.FILES.get('file').name)
    )
    uploaded_file.save()
    return JsonResponse({"file_id": uploaded_file.id})


def get_intersection_of_file_endings_from_different_input_filetypes(
        list_of_file_types_per_file_grouped_by_plugin: list[dict]
) -> dict:
    """
    :param list_of_file_types_per_file_grouped_by_plugin:
    :example [{"plugin_name":["1","2","3"]},{"plugin_name":["1","2","4"], "another_plugin":["1","2"]}]
    :return: intersection of plugins and their values, in this example: {"plugin_name":["1","2"]}
    """
    if len(list_of_file_types_per_file_grouped_by_plugin) == 0:
        return dict()

    # Initialize the result dictionary with the first plugin's data
    result = list_of_file_types_per_file_grouped_by_plugin[0]

    for plugin_data in list_of_file_types_per_file_grouped_by_plugin[1:]:
        for plugin, file_types in plugin_data.items():
            # If the plugin exists in the result and has matching values, keep the intersection
            if plugin in result:
                result[plugin] = list(set(result[plugin]) & set(file_types))

    # Remove plugins with empty intersections
    result = {plugin: file_types for plugin, file_types in result.items() if file_types}

    return result


# TODO move to proper test file
def test_get_intersections():
    result = get_intersection_of_file_endings_from_different_input_filetypes(
        [
            {"plugin1": [1, 3, 4, 5, 6, 7, 8, 9], "Plugin3": [1, 2, 3, 4, 5, 6, 7, 8, 9],
             "plugin2": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
            {"Plugin7": [1, 2, 3, 4, 5, 6, 7, 8, 9], "plugin2": [1, 2, 3, 4, 5, 6, 9],
             "plugin1": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
            {"Plugin7": [1, 2, 3, 4, 5, 6, 7, 8, 9], "plugin2": [1, 2, 3, 4, 5, 6, 7, 8],
             "plugin1": [1, 2, 3, 4, 5, 6, 7, 8, 9],
             "Plugin8": [1, 2, 3, 4, 5, 6, 7, 8, 9]}
        ]
    )
    assert result == {'plugin1': {1, 3, 4, 5, 6, 7, 8, 9}, 'plugin2': {1, 2, 3, 4, 5, 6}}


@require_http_methods(["GET"])
@requires_parameters("GET", ["plugin", "destination_file_type"])
def get_form_html_for_web_view(request):
    if not is_valid_plugin(request.GET.get("plugin")):
        return invalid_parameter_error("plugin")
    try:
        destination_file_type = request.GET.get("destination_file_type")
        plugin = Plugin.get_processing_plugin_by_name(request.GET.get("plugin"))
        if destination_file_type not in plugin.get_destination_types():
            raise ValueError("No support for the given Value. Plugin:", plugin.name, "Value:", destination_file_type)
        form_html, form_script = plugin.get_form_html_and_script(destination_file_type)
        return JsonResponse({
            "status": 200,
            "form_html": form_html,
            "form_script": form_script
        }, status=200)
    except ValueError as e1:
        if settings.DEBUG:
            raise e1
        return invalid_parameter_error("destination_file_type")
    except ImportError as error:
        if settings.DEBUG:
            raise error
        return internal_server_error(str(error))


def is_valid_plugin(plugin):
    return plugin in [p.name for p in settings.PROCESSOR_PLUGINS]


@require_http_methods(["GET"])
@requires_parameters("GET", ["plugin", "destination_file_type"])
def get_settings_config_for_processor(request):
    if not is_valid_plugin(request.GET.get("plugin")):
        print(request.GET.get("plugin"))
        return invalid_parameter_error("plugin")
    try:
        # destination_file_type = "*"  # request.GET.get("destination_file_type")
        plugin = Plugin.get_processing_plugin_by_name(request.GET.get("plugin"))
        #   if destination_file_type not in plugin.get_destination_types():
        #     raise ValueError("No support for the given Value. Plugin:", plugin.name, "Value:", destination_file_type)

        form = plugin.get_form_class()()

        def get_value_from_field_if_it_exists(field, name: str, attr: str):
            # helps to map the django internal keys to the ones used in the frontend formular
            return {"" + name: getattr(field, attr)} if hasattr(field, attr) else {}

        advanced_form_fields = form.get_advanced_options()
        hierarchy = form.get_hierarchy()
        form_data = {
            "fields": [
                {
                    "name": field_name,
                    "type": field.widget.input_type,
                    **get_value_from_field_if_it_exists(field, "label", "label"),
                    **get_value_from_field_if_it_exists(field, "value", "initial"),
                    **get_value_from_field_if_it_exists(field, "step", "step_size"),
                    **get_value_from_field_if_it_exists(field, "min", "min_value"),
                    **get_value_from_field_if_it_exists(field, "max", "max_value"),
                    **get_value_from_field_if_it_exists(field, "help_text", "help_text"),
                    "choices": [{"value": value, "display": display} for value, display in
                                field.choices] if hasattr(field, "choices") else []
                }
                for field_name, field in form.fields.items()
            ]
        }

        return JsonResponse({
            "status": 200,
            "config": {
                "form_data": form_data,
                "advanced_form_fields": advanced_form_fields,
                "hierarchy": hierarchy
            }
        }, status=200)
    except ValueError as e1:
        if settings.DEBUG:
            raise e1
        return invalid_parameter_error("destination_file_type")
    except ImportError as error:
        if settings.DEBUG:
            raise error
        return internal_server_error(str(error))


@require_http_methods(["GET"])
def get_possible_destination_file_types(request):
    from_file_types = []
    if "file_ids" in request.GET and request.GET.get("file_ids") != "":
        file_ids = request.GET.get("file_ids").split(",")
        for file_id in file_ids:
            file = UploadedFile.objects.get(
                id=file_id,
                user_id=request.session.get("user_id")
            )
            from_file_types.append(file.get_mime_type())

    if len(from_file_types) == 0:
        from_file_types = [None]

    list_of_file_types_per_file = list()
    list_of_mergers = dict()
    for from_file_type in from_file_types:
        list_of_file_types = dict()
        for plugin in settings.PROCESSOR_PLUGINS:
            list_of_file_types[plugin.name] = plugin.get_destination_types(from_file_type)
            list_of_mergers[plugin.name] = plugin.is_merger()
        list_of_file_types_per_file.append(list_of_file_types)
        # TODO also allow multi steps convert -> shortest path inside graph
    return JsonResponse({
        "status": 200,
        "possible_file_types": get_intersection_of_file_endings_from_different_input_filetypes(
            list_of_file_types_per_file),
        "input_file_types": {plugin.name: plugin.get_input_file_types() for plugin in settings.PROCESSOR_PLUGINS},
        "list_of_mergers": list_of_mergers
    }, status=200)


@require_http_methods(["GET"])
def get_possible_destination_file_types_by_file_id(request, file_id):
    file_mime_type = UploadedFile.objects.get(id=file_id).get_mime_type()

    list_of_file_types = dict()
    list_of_mergers = dict()
    for plugin in settings.PROCESSOR_PLUGINS:
        list_of_file_types[plugin.name] = plugin.get_destination_types(file_mime_type)
        list_of_mergers[plugin.name] = plugin.is_merger()

    return JsonResponse({
        "status": 200,
        "possible_file_types": list_of_file_types,
        "list_of_mergers": list_of_mergers
    }, status=200)


@csrf_protect
@require_http_methods(["POST"])
def process_files(request):
    POST_DATA = json.loads(request.body)
    processing_request = ProcessingFilesRequest.get_or_create_new_request(
        user_id=request.session["user_id"],
        request_id=get_random_string(50)
    )

    file_ids = json.loads(POST_DATA.get("files"))
    files = []
    for file_id in file_ids:
        file = UploadedFile.objects.get(id=file_id)
        file.processing_request = processing_request
        file.save()
        files.append(file)

    *plugin_name, result_file_type = POST_DATA.get("processor").split("-")
    plugin = Plugin.get_processing_plugin_by_name("-".join(plugin_name))

    input_file_list = UploadedFile.get_uploaded_file_list_of_current_request(processing_request)
    if len(input_file_list) < 1:
        return JsonResponse({"status": 412, "error": "No files were found for this request."}, status=412)

    _request_parameters = {**POST_DATA, "result_file_type": result_file_type}

    _source_path = os.path.join(MEDIA_ROOT, processing_request.get_source_dir())

    paths = []

    if not os.path.exists(_source_path):
        os.mkdir(_source_path)
    for file in files:
        print(file.id)
        print(os.path.join(MEDIA_ROOT, file.uploaded_file.name), _source_path)
        shutil.copy(os.path.join(MEDIA_ROOT, file.uploaded_file.name), _source_path)
        paths.append(os.path.join(_source_path, os.path.basename(file.uploaded_file.name)))
    print(paths)

    # destination is either merged file or directory
    _destination_path = "merge" if _request_parameters.get("merge_files") else "default"

    task = plugin.get_task()

    processing_request = processing_request

    if _destination_path == "merge":
        _destination_path = ""
    elif _destination_path == "default":
        _destination_path = _source_path + "_processed"
    if not os.path.isdir(_destination_path):
        os.mkdir(_destination_path)

    print(_request_parameters,
          paths, _destination_path)

    celery_task = task.delay(request_parameters=_request_parameters,
                             files=paths, destination_path=_destination_path)

    processing_request.celery_task_id = celery_task
    processing_request.save()
    print("TASK", celery_task)
    # processing_request.task_id = task_id
    processing_request.save()
    return JsonResponse({"processing_request_id": processing_request.id})
