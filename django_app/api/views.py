from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django_app import settings
from django_app.plugin_system.plugin import Plugin
from django_app.webserver.models.processed_file import ProcessedFile
from django_app.webserver.models.processing_files_request import ProcessingFilesRequest
from django_app.webserver.models.uploaded_file import UploadedFile
from django_app.webserver.validators import get_file_extension


# TODO favicon.ico
# TODO move valid_file_endings from UploadedFile -> request Table
# TODO decorator for method type

@csrf_protect
def get_all_files(request):
    if request.method == "GET":
        files_json = ProcessedFile.get_all_processing_files(request.session["user_id"])
        return JsonResponse({"status": 200, "files": files_json}, status=200)
    return wrong_method_error("GET")


def wrong_method_error(*allowed_methods):
    method_hint = "".join(("Try using " if i == 0 else "or") + allowed_methods[i] for i in range(len(allowed_methods)))
    return JsonResponse({"status": 405, "error": "Method Not Allowed. " + method_hint}, status=405)


def parameter_missing_error(parameter_name: str):
    return JsonResponse({"status": 412, "error": f"Parameter '{parameter_name}' is required!"}, status=412)


def invalid_parameter_error(parameter_name: str):
    return JsonResponse({"status": 412, "error": f"Invalid value for parameter '{parameter_name}"}, status=412)


def internal_server_error(error_string: str):
    return JsonResponse({"status": 500, "error": error_string}, status=500)


# TODO /api/rename_file

@csrf_protect  # TODO csrf_protect doesn't work, yet
def remove_file(request):
    if request.method != "GET":
        return wrong_method_error("GET")

    if request.GET.get("file_origin") == "uploaded":
        file_class = UploadedFile
    elif request.GET.get("file_origin") == "processed":
        file_class = ProcessedFile
    else:
        return JsonResponse({"status": 412, "error": "Parameter file_origin is required."}, status=412)

    file = file_class.objects.filter(
        id=request.GET.get("file_id")
    ).first()

    if file is not None and file.processing_request.user_id == request.session["user_id"]:
        file.delete()
    else:
        return JsonResponse({"status": 412, "error": "No file with that id found for you."}, status=412)
    return JsonResponse({"status": 200, "success": "Removed file successfully."}, status=200)


@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        request_id = request.POST.get('request_id')
        uploaded_file = UploadedFile(
            uploaded_file=request.FILES.get('file'),
            processing_request=ProcessingFilesRequest.get_or_create_new_request(user_id, request_id),
            valid_file_endings=get_file_extension(request.FILES.get('file').name)
        )
        uploaded_file.save()
        file_id = uploaded_file.id
        return JsonResponse({"file_id": file_id})
    return wrong_method_error("POST")


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
    # get intersecting plugins from all list entries
    plugin_intersections = set.intersection(
        *[set(types_of_file.keys()) for types_of_file in list_of_file_types_per_file_grouped_by_plugin]
    )
    list_of_value_intersections_of_plugin_per_file = [
        {
            plugin: file[plugin]
            for plugin in file.keys()
            if plugin in plugin_intersections
        } for file in list_of_file_types_per_file_grouped_by_plugin
    ]
    intersections = dict()
    for plugin in list_of_value_intersections_of_plugin_per_file[0].keys():
        buffer = list()
        for file_endings in list_of_value_intersections_of_plugin_per_file:
            if len(file_endings[plugin]) > 0:
                buffer.append(set(file_endings[plugin]))
        if len(buffer) > 0:
            intersections[plugin] = list(set.intersection(*buffer))
    return intersections


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


def get_form_html_for_web_view(request):
    if request.method != "GET":
        return wrong_method_error("GET")
    elif "plugin" not in request.GET:
        return parameter_missing_error("plugin")
    elif "destination_file_type" not in request.GET:
        return parameter_missing_error("destination_file_type")
    elif request.GET.get("plugin") not in [p.name for p in settings.PROCESSOR_PLUGINS]:
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
            "form_script": form_script,
            "allowed_file_endings": plugin.get_input_file_types()
        }, status=200)
    except ValueError as e1:
        if settings.DEBUG:
            print(e1)
        return invalid_parameter_error("destination_file_type")
    except ImportError as error:
        if settings.DEBUG:
            print(error)
        return internal_server_error(str(error))


def get_possible_destination_file_types(request):
    if request.method != "GET":
        return wrong_method_error("GET")

    from_file_types = []
    if "request_id" in request.GET:
        request_id = request.GET.get("request_id")
        request = ProcessingFilesRequest.get_or_create_new_request(
            user_id=request.session.get("user_id"),
            request_id=request_id
        )
        files_of_request = UploadedFile.get_uploaded_file_list_of_current_request(request)
        from_file_types = [
            file.get_mime_type() for file in files_of_request
        ]

    if len(from_file_types) == 0:
        from_file_types = [None]

    list_of_file_types_per_file = list()
    for from_file_type in from_file_types:
        list_of_file_types = dict()
        for plugin in settings.PROCESSOR_PLUGINS:
            list_of_file_types[plugin.name] = plugin.get_destination_types(from_file_type)
        list_of_file_types_per_file.append(list_of_file_types)
        # TODO also allow multi steps convert -> shortest path inside graph
    return JsonResponse({
        "status": 200,
        "list_of_file_types_per_file": list_of_file_types_per_file,
        "possible_file_types": get_intersection_of_file_endings_from_different_input_filetypes(
            list_of_file_types_per_file)
    }, status=200)
