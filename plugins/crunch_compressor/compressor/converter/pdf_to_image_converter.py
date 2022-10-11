from django_app.plugin_system.processing_classes.converter import Converter
from plugins.crunch_compressor.utility.console_utility import ConsoleUtility

import os

# package name PyMuPdf
import fitz


class PdfToImageConverter(Converter):
    SUPPORTED_FILETYPES = ["png", "pnm", "pgm", "pbm", "ppm", "pam", "psd", "ps"]  # TODO test all possible types

    def __init__(
            self,
            file_type_to: str,
            dpi: int = 400,
            event_handlers=None
    ):
        if file_type_to.lower() not in self.SUPPORTED_FILETYPES:
            raise ValueError(f"{file_type_to} is not supported.")
        super().__init__(event_handlers, "pdf", file_type_to, False, True)
        if dpi < 0:
            raise ValueError("default dpi needs to be greater than 0")
        self.__dpi = dpi

    def process_file(self, source_file: str, destination_file: str) -> None:
        # create destination directory if not already exists
        os.makedirs(destination_file, exist_ok=True)

        ConsoleUtility.print("--splitting pdf into images--")

        # open pdf and split it into rgb-pixel maps -> png
        doc = fitz.open(source_file)
        for page in doc:
            ConsoleUtility.print(f"** - Finished Page {page.number + 1}/{len(doc)}")
            pix = page.get_pixmap(dpi=self.__dpi)
            page_number = str(page.number) if page.number >= 10 else "0" + str(page.number)
            pix.save(os.path.join(destination_file, 'page_%s.%s' % (page_number, self._file_type_to)))
