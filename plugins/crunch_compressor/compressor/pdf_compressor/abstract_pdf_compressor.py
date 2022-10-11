import os
from abc import ABC

import fitz

from django_app.plugin_system.processing_classes.compressor import Compressor


class AbstractPdfCompressor(Compressor, ABC):
    def __init__(
            self,
            event_handlers=None,
            run_multi_threaded: bool = True,
    ):
        super().__init__(event_handlers, "pdf", "pdf", True, run_multi_threaded)

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        merger = fitz.open()
        for file in file_list:
            if os.path.exists(self._final_merge_file):
                with fitz.open(self._final_merge_file) as f:
                    merger.insert_pdf(f)
            with fitz.open(file) as f:
                merger.insert_pdf(f)
            os.remove(file)
        merger.save(self._final_merge_file)
