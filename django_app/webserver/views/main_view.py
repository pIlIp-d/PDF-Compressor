from functools import reduce

from django.shortcuts import render
from django.template import loader

from django_app.webserver.forms.image_convert_form import ImageConvertForm, allowed_file_endings
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
        "extra_scripts": ["pdf_compression.js"],
        "form_html": loader.get_template('application/forms/pdf_compression_form.html').render({"form": form})
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
        "extra_scripts": [],
        "form_html": loader.get_template('application/forms/png_compression_form.html').render({"form": form})
    }
    return render(request, 'application/main.html', context)


def render_image_convert_view(request):
    form = ImageConvertForm()
    relative_dir = get_directory_for_html(request)
    context = {
        "dir": relative_dir,
        "processing_action": "start_png_compression/",
        "allowed_file_endings": ",".join(allowed_file_endings),
        "user_id": request.session["user_id"],
        "extra_scripts": [],
        "form_html": loader.get_template('application/forms/image_convert_form.html').render({"form": form})
    }
    print([(i, ending) for i, ending in zip(range(len(allowed_file_endings)), allowed_file_endings)])
    return render(request, 'application/main.html', context)
