from plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder

import os

# package name PyMuPdf
import fitz


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
        super().__init__(event_handlers, ["pdf"], file_type_to, False, True)
        if dpi < 0:
            raise ValueError("default dpi needs to be greater than 0")
        self.__dpi = dpi

    def process_file(self, source_file: str, destination_path: str) -> None:
        # create destination directory if not already exists
        # TODO create preprocessor/postprocessors for console output
        print("--splitting pdf into images--")

        # open pdf and split it into rgb-pixel maps -> png
        doc = fitz.open(source_file)
        chars_needed_for_highest_page_number = len(str(len(doc)))

        def get_page_number_string(page_num: int) -> str:
            raw_num = str(page_num)
            return "0" * (chars_needed_for_highest_page_number - len(raw_num)) + raw_num

        for page in doc:
            print(f"** - Finished Page {page.number + 1}/{len(doc)}")
            pix = page.get_pixmap(dpi=self.__dpi)
            page_number = get_page_number_string(page.number + 1)
            pix.save(os.path.join(destination_path, '%s_page_%s.%s' %
                                  (self._get_filename(source_file), page_number, self._file_type_to)))
