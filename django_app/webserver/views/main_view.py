from django.shortcuts import render

from django_app.webserver.forms import PdfCompressorForm


def render_main_view(request):
    allowed_file_endings = [".pdf", ".png"]  # no ',' allowed in file ending
    form = PdfCompressorForm()
    dir = "/".join([".." for _ in range(len(request.META['PATH_INFO'].split("/"))-2)])
    print(dir)
    context = {
        "dir": dir + "/",
        "allowed_file_endings": ",".join(allowed_file_endings),
        "form": form,
        "user_id": request.session["user_id"],
    }
    return render(request, 'application/main.html', context)
