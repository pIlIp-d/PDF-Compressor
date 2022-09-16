from django_app.task_scheduler.processing_task import ProcessingTask
from pdfcompressor.pdfcompressor import PDFCompressor


class PdfCompressionTask(ProcessingTask):
    TASK_TYPE = "PdfCompressionTask"

    def __init__(self, request_id: int, amount_of_input_files: int, processed_file_paths: list, task_id: int = None,
                 finished: bool = False, **kwargs):
        print("created")
        super().__init__(request_id, amount_of_input_files, processed_file_paths, self.TASK_TYPE, task_id, finished,
                         **kwargs)

    def run(self):
        print("Finished task" + str(self.task_id))
        event_handler = [super()._get_process_stats_event_handler()]
        PDFCompressor(event_handler=event_handler, **self._parameters).compress()
        self.finish_task()
