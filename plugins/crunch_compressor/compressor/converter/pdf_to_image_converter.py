from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder
from django_app.utility.console_utility import ConsoleUtility

import os

# package name PyMuPdf
import fitz

from django_app.utility.os_utility import OsUtility


class PdfToImageConverter(ProcessorWithDestinationFolder):
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

    def process_file(self, source_file: str, destination_path: str) -> None:
        # create destination directory if not already exists
        os.makedirs(destination_path, exist_ok=True)

        print("METHODE", source_file, destination_path)
        ConsoleUtility.print("--splitting pdf into images--")

        # open pdf and split it into rgb-pixel maps -> png
        doc = fitz.open(source_file)
        for page in doc:
            ConsoleUtility.print(f"** - Finished Page {page.number + 1}/{len(doc)}")
            pix = page.get_pixmap(dpi=self.__dpi)
            page_number = str(page.number + 1) if page.number + 1 >= 10 else "0" + str(
                page.number + 1)  # TODO support pages/ numbers over 100 properly
            pix.save(os.path.join(destination_path, '%s_page_%s.%s' %
                                  (OsUtility.get_filename(source_file), page_number, self._file_type_to)))
