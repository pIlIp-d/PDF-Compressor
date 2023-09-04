import mimetypes

from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from plugin_system.plugins.crunch_compressor.converter.images_to_pdf_converter import ImagesToPdfConverter
from plugin_system.plugins.crunch_compressor.converter.pdf_to_image_converter import PdfToImageConverter
from plugin_system.plugins.crunch_compressor.compressor.pdf_compressor.pdf_crunch_compressor import PDFCrunchCompressor
from plugin_system.plugins.crunch_compressor.compressor.png_compressor.png_crunch_compressor import PNGCrunchCompressor
from plugin_system.plugins.crunch_compressor.config import get_config


class PdfCompressionTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        PDFCrunchCompressor(
            compression_mode=int(self._request_parameters.get("compression_mode")),
            force_ocr=self._request_parameters.get("ocr_mode") == "on",
            no_ocr=self._request_parameters.get("ocr_mode") == "off",
            tesseract_language=self._request_parameters.get("tesseract_language"),
            simple_and_lossless=self._request_parameters.get("simple_and_lossless") == "on",
            default_pdf_dpi=int(self._request_parameters.get("default_pdf_dpi")),
            event_handlers=event_handler
        ).process(
            self._source_path,
            self._destination_path
        )


class PngCompressionTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        config = get_config()
        PNGCrunchCompressor(
            pngquant_path=config.pngquant_path,
            advpng_path=config.advpng_path,
            pngcrush_path=config.pngcrush_path,
            compression_mode=int(self._request_parameters.get("compression_mode")),
            event_handlers=event_handler
        ).process(
            source_path=self._source_path,
            destination_path=self._destination_path
        )


class ImageToPdfConvertTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        config = get_config()
        ImagesToPdfConverter(
            pytesseract_path=config.tesseract_path,
            force_ocr=self._request_parameters.get("ocr_mode") == "on",
            no_ocr=self._request_parameters.get("ocr_mode") == "off",
            tesseract_language=self._request_parameters.get("tesseract_language"),
            tessdata_prefix=config.tessdata_prefix,
            event_handlers=event_handler
        ).process(
            source_path=self._source_path,
            destination_path=self._destination_path
        )


class PdfToImageConvertTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        PdfToImageConverter(
            mimetypes.guess_extension(self._request_parameters.get("result_file_type"))[1:],
            int(self._request_parameters.get("default_pdf_dpi")),
            event_handlers=event_handler
        ).process(
            source_path=self._source_path,
            destination_path=self._destination_path if self._destination_path == "merge" else "default"
        )
