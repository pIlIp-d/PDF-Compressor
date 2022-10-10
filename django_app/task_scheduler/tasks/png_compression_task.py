from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from django_app.webserver.custom_models.string_utility import StringUtility
from django_app.webserver.models import ProcessingFilesRequest
from pdfcompressor.compressor.png_compressor.png_crunch_compressor import PNGCrunchCompressor
from pdfcompressor.utility.os_utility import OsUtility


class PngCompressionTask(ProcessingTask):
    def __init__(
            self,
            request_parameters,
            processing_request: ProcessingFilesRequest,
            processed_file_paths: list
    ):
        super().__init__(processing_request, processed_file_paths)
        self.__source_path = StringUtility.get_local_absolute_path(processing_request.get_source_dir())
        self.__destination_path = StringUtility.get_local_absolute_path(processing_request.get_destination_dir())
        self.__compression_mode = int(request_parameters.get("compression_mode"))

    def run(self):
        event_handler = super()._get_process_stats_event_handler()
        config = OsUtility.get_config()
        PNGCrunchCompressor(
            pngquant_path=config.pngquant_path,
            advpng_path=config.advpng_path,
            pngcrush_path=config.pngcrush_path,
            compression_mode=self.__compression_mode,
            event_handlers=event_handler,
        ).compress(self.__source_path, self.__destination_path)
        self.finish_task()
