import os
from abc import ABC

import fitz

from ...compressor.compressor import Compressor
from ...utility.EventHandler import EventHandler


class AbstractPdfCompressor(Compressor, ABC):
    def __init__(self, event_handlers: list[EventHandler] = list()):
        super().__init__(event_handlers, "pdf", "pdf", True)

    def postprocess(self, source_file: str, destination_file: str) -> None:
        if self._final_merge_file is not None:
            # merge new file into pdf (final_merge_file)
            merger = fitz.open()
            if os.path.exists(self._final_merge_file):
                with fitz.open(self._final_merge_file) as f:
                    merger.insert_pdf(f)
            with fitz.open(destination_file) as f:
                merger.insert_pdf(f)
            merger.save(self._final_merge_file)
