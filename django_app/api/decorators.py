from functools import wraps

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse


def requires_parameters(allowed_methods: str, list_of_required_parameters: list[str]):
    def decorator(func):
        @wraps(func)
        def handling(request, *args, **kwargs):
            if hasattr(request, allowed_methods):
                parameter_list = getattr(request, allowed_methods)
                # check if any parameters are missing in the parameters of a specific request method
                for parameter in list_of_required_parameters:
                    if parameter not in parameter_list:
                        return JsonResponse({"status": 412, "error": f"Parameter '{parameter}' is required!"},
                                            status=412)
            else:
                raise ValueError("unknown method")
            return func(request, *args, **kwargs)
        return handling
    return decorator


def only_for_localhost(func):
    def run_decorated_func(request, *args, **kwargs):
        if isinstance(request, WSGIRequest) and request.META.get("REMOTE_ADDR") == "127.0.0.1":
            return func(request, *args, **kwargs)
        else:
            return JsonResponse({"status": 401, "error": "Your can't access this request."}, status=401)

    return run_decorated_func
