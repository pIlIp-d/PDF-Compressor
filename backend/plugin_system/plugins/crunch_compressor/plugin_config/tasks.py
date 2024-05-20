import mimetypes

from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from filecrusher import ImagesToPdfConverter, PDFCompressor, PdfToImageConverter, PNGCompressor, CPdfSqueezeCompressor


class PdfCompressionTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        if self._request_parameters.get("simple_and_lossless") == "on":
            processor = CPdfSqueezeCompressor(event_handlers=event_handler)
        else:
            processor = PDFCompressor(
                compression_mode=int(self._request_parameters.get("compression_mode")),
                force_ocr=self._request_parameters.get("ocr_mode") == "on",
                no_ocr=self._request_parameters.get("ocr_mode") == "off",
                tesseract_language=self._request_parameters.get("tesseract_language"),
                default_pdf_dpi=int(self._request_parameters.get("default_pdf_dpi")),
                event_handlers=event_handler
            )
        processor.process_file(
            self._source_path,
            self._destination_path
        )


class PngCompressionTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        PNGCompressor(
            compression_mode=int(self._request_parameters.get("compression_mode")),
            event_handlers=event_handler
        ).process_file(
            source_path=self._source_path,
            destination_path=self._destination_path
        )


class ImageToPdfConvertTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        ImagesToPdfConverter(
            force_ocr=self._request_parameters.get("ocr_mode") == "on",
            no_ocr=self._request_parameters.get("ocr_mode") == "off",
            tesseract_language=self._request_parameters.get("tesseract_language"),
            event_handlers=event_handler
        ).process_file(
            source_path=self._source_path,
            destination_path=self._destination_path
        )


class PdfToImageConvertTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_event_handler()
        PdfToImageConverter(
            file_type_to=mimetypes.guess_extension(self._request_parameters.get("result_file_type"))[1:],
            dpi=int(self._request_parameters.get("default_pdf_dpi")),
            event_handlers=event_handler
        ).process_file(
            source_path=self._source_path,
            destination_path=self._destination_path if self._destination_path == "merge" else "default"
        )
