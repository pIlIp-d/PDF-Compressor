from functools import reduce

from django.shortcuts import render

from django_app.webserver.forms import PdfCompressorForm


def render_main_view(request):
    allowed_file_endings = [".pdf", ".png"]  # no ',' allowed in file ending
    form = PdfCompressorForm()
    relative_dir = reduce(
        lambda dir_string, _: ".." + dir_string,
        range(len(request.META['PATH_INFO'].split("/"))-2),
        "/"
    )
    context = {
        "dir": relative_dir,
        "allowed_file_endings": ",".join(allowed_file_endings),
        "form": form,
        "user_id": request.session["user_id"],
    }
    return render(request, 'application/main.html', context)