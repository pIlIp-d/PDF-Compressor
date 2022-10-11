from abc import ABC

from django_app.plugin_system.processing_classes.processor import Processor


class Compressor(Processor, ABC):

    def __init__(
            self,
            event_handlers,
            file_type_from: str,
            file_type_to: str,
            can_merge: bool = False,
            run_multi_threaded: bool = True,
            processed_part: str = "All Files"
    ):
        super().__init__(
            event_handlers,
            file_type_from,
            file_type_to,
            "_compressed",  # predefine file appendix
            can_merge,
            run_multi_threaded,
            processed_part
        )
