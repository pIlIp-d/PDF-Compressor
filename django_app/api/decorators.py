from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse


def only_for_localhost(func):
    def run_decorated_func(*args, **kwargs):
        request = args[0]
        print(request.META.get("REMOTE_ADDR"))
        if isinstance(request, WSGIRequest) and request.META.get("REMOTE_ADDR") == "127.0.0.1":
            return func(*args, **kwargs)
        else:
            return JsonResponse({"status": 401, "error": "Your can't access this request."}, status=401)

    return run_decorated_func
