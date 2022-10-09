from django_app import settings
from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from django_app.webserver.custom_models.string_utility import StringUtility
from django_app.webserver.models import ProcessingFilesRequest
from pdfcompressor.pdfcompressor import PDFCompressor


class PdfCompressionTask(ProcessingTask):
    def __init__(
            self,
            request_parameters,
            processing_request: ProcessingFilesRequest,
            processed_file_paths: list
    ):
        print("CONSTRUCTED")
        super().__init__(processing_request, processed_file_paths)
        self.__source_path = StringUtility.get_local_relative_path(processing_request.get_source_dir())
        # destination is either merged file or directory
        self.__destination_path = StringUtility.get_local_relative_path(
            processed_file_paths[-1] if request_parameters.get(
                "merge_files") else processing_request.get_destination_dir()
        )
        self.__compression_mode = int(request_parameters.get("compression_mode"))
        self.__force_ocr = True if request_parameters.get("ocr_mode") == "on" else False
        self.__no_ocr = True if request_parameters.get("ocr_mode") == "off" else False
        self.__tesseract_language = request_parameters.get("tesseract_language")
        self.__simple_and_lossless = True if request_parameters.get("simple_and_lossless") == "on" else False
        self.__default_pdf_dpi = int(request_parameters.get("default_pdf_dpi"))

    def run(self):
        event_handler = super()._get_process_stats_event_handler()
        PDFCompressor(
            source_path=self.__source_path,
            destination_path=self.__destination_path,
            compression_mode=self.__compression_mode,
            force_ocr=self.__force_ocr,
            no_ocr=self.__no_ocr,
            quiet=not settings.DEBUG,
            tesseract_language=self.__tesseract_language,
            simple_and_lossless=self.__simple_and_lossless,
            default_pdf_dpi=self.__default_pdf_dpi,
            event_handlers=event_handler
        ).compress()
        self.finish_task()
