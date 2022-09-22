from functools import reduce

from django.shortcuts import render

from django_app.webserver.forms.pdf_compressor_form import PdfCompressorForm
from django_app.webserver.forms.png_compressor_form import PngCompressorForm


def get_directory_for_html(request) -> str:
    return reduce(
        lambda dir_string, _: ".." + dir_string,
        range(len(request.META['PATH_INFO'].split("/")) - 2),
        "/"
    )


def render_main_view(request):
    allowed_file_endings = [".pdf"]  # no ',' allowed in file ending
    form = PdfCompressorForm()
    relative_dir = get_directory_for_html(request)
    context = {
        "dir": relative_dir,
        "processing_action": "start_pdf_compression/",
        "allowed_file_endings": ",".join(allowed_file_endings),
        "form": form,
        "user_id": request.session["user_id"],
    }
    return render(request, 'application/main.html', context)


def render_png_compression_view(request):
    allowed_file_endings = [".png"]  # no ',' allowed in file ending
    form = PngCompressorForm()
    relative_dir = get_directory_for_html(request)
    context = {
        "dir": relative_dir,
        "processing_action": "start_png_compression/",
        "allowed_file_endings": ",".join(allowed_file_endings),
        "form": form,
        "user_id": request.session["user_id"],
    }
    return render(request, 'application/main.html', context)
