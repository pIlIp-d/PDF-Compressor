from functools import reduce

from django.forms import Form
from django.shortcuts import render
from django.template import loader

from django_app.webserver.forms import image_convert_form
from django_app.webserver.forms.image_convert_form import ImageConvertForm
from django_app.webserver.forms.pdf_compressor_form import PdfCompressorForm
from django_app.webserver.forms.png_compressor_form import PngCompressorForm


def get_directory_for_html(request) -> str:
    return reduce(
        lambda dir_string, _: ".." + dir_string,
        range(len(request.META['PATH_INFO'].split("/")) - 2),
        "/"
    )


def custom_form_renderer(form: Form) -> str:
    html = ""
    for form_element in form:
        html += f"""
        <div class="form_element" id="id_{ form_element.name }">
            <span class="helptext">{ form_element.help_text }</span>
            <span>{ form_element.label }</span>
            { form_element }
        </div>
        """
    return html


def render_main_view(request):
    return get_processing_view(
        request,
        PdfCompressorForm(),
        "start_pdf_compression/",
        [".pdf"],
        ["pdf_compression.js"],
    )


def render_png_compression_view(request):
    return get_processing_view(
        request,
        PngCompressorForm(),
        "start_png_compression/",
        [".png"]
    )


def render_image_convert_view(request):
    return get_processing_view(
        request,
        ImageConvertForm(),
        "start_png_compression/",  # TODO
        image_convert_form.allowed_file_endings
    )


def get_processing_view(
        request,
        form_html: Form,
        processing_action: str,
        allowed_file_endings: list,
        extra_scripts=None
):
    if extra_scripts is None:
        extra_scripts = list()

    context = {
        "dir": get_directory_for_html(request),
        "processing_action": processing_action,
        "allowed_file_endings": ",".join(allowed_file_endings),  # no ',' allowed in file ending
        "user_id": request.session["user_id"],
        "extra_scripts": extra_scripts,
        "form_html": custom_form_renderer(form_html),
        "request_id": request.session["request_id"]
    }
    return render(request, 'application/main.html', context)
