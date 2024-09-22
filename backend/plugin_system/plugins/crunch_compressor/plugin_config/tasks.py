import mimetypes
import os

from celery import shared_task
from filecrusher import ImagesToPdfConverter, PDFCompressor, PdfToImageConverter, PNGCompressor, CPdfSqueezeCompressor, batch_process_files_async
from asgiref.sync import async_to_sync


@shared_task
def pdfCompressionTask(request_parameters, files, destination_path):
    print(os.path.exists(files[0]))
    print(files[0].endswith(".pdf"))

    if request_parameters.get("simple_and_lossless") == "on":
        processor = CPdfSqueezeCompressor()
    else:
        processor = PDFCompressor(
            compression_mode=int(request_parameters.get("compression_mode")),
            force_ocr=request_parameters.get("ocr_mode") == "on",
            no_ocr=request_parameters.get("ocr_mode") == "off",
            tesseract_language=request_parameters.get("tesseract_language"),
            default_pdf_dpi=int(request_parameters.get("default_pdf_dpi")),
        )
    async_to_sync(batch_process_files_async)(files, destination_path, processor)


@shared_task
def pngCompressionTask(request_parameters, files, destination_path):
    processor = PNGCompressor(
        compression_mode=int(request_parameters.get("compression_mode")),
    )
    async_to_sync(batch_process_files_async)(files, destination_path, processor)


@shared_task
def imageToPdfConvertTask(request_parameters, files, destination_path):
    processor = ImagesToPdfConverter(
        force_ocr=request_parameters.get("ocr_mode") == "on",
        no_ocr=request_parameters.get("ocr_mode") == "off",
        tesseract_language=request_parameters.get("tesseract_language"),
    )
    async_to_sync(batch_process_files_async)(files, destination_path, processor)


@shared_task
def pdfToImageConvertTask(request_parameters, files, destination_path):
    processor = PdfToImageConverter(
        file_type_to=mimetypes.guess_extension(request_parameters.get("result_file_type"))[1:],
        dpi=int(request_parameters.get("default_pdf_dpi")),
    )
    async_to_sync(batch_process_files_async)(files, destination_path, processor)
