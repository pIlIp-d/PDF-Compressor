from django_app.task_scheduler.tasks.processing_task import ProcessingTask
from pdfcompressor.compressor.png_compressor.png_crunch_compressor import PNGCrunchCompressor
from pdfcompressor.utility.os_utility import OsUtility


class PngCompressionTask(ProcessingTask):

    def run(self):
        event_handler = super()._get_process_stats_event_handler()
        source_path = self._parameters.pop("source_path")
        destination_path = self._parameters.pop("destination_path")
        config = OsUtility.get_config()
        PNGCrunchCompressor(
            config.pngquant_path,
            config.advpng_path,
            config.pngcrush_path,
            event_handlers=event_handler,
            **self._parameters
        ).compress(source_path, destination_path)
        self.finish_task()
