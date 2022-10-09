from functools import reduce

from django.shortcuts import render


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
