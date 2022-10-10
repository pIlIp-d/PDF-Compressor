from django_app import settings
from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from plugins.pdfcompressor.pdfcompressor import PDFCompressor


class PdfCompressionTask(ProcessingTask):
    def run(self):
        event_handler = super()._get_process_stats_event_handler()
        PDFCompressor(
            source_path=self._source_path,
            destination_path=self._destination_path,
            compression_mode=int(self._request_parameters.get("compression_mode")),
            force_ocr=self._request_parameters.get("ocr_mode") == "on",
            no_ocr=self._request_parameters.get("ocr_mode") == "off",
            quiet=not settings.DEBUG,
            tesseract_language=self._request_parameters.get("tesseract_language"),
            simple_and_lossless=self._request_parameters.get("simple_and_lossless") == "on",
            default_pdf_dpi=int(self._request_parameters.get("default_pdf_dpi")),
            event_handlers=event_handler
        ).compress()
        self.finish_task()
