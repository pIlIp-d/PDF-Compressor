from plugins.crunch_compressor.utility.console_utility import ConsoleUtility

import os

# package name PyMuPdf
import fitz


class PdfToImageConverter(Converter):
    def __init__(
            self,
            origin_path: str,
            dest_path: str,
            dpi: int = 400,
            event_handlers: list[EventHandler] = list()
    ):
        super().__init__(origin_path, dest_path, event_handlers)

        if dpi < 0:
            raise ValueError("default dpi needs to be greater than 0")
        self.__dpi = dpi

    def convert(self) -> None:
        os.makedirs(self.dest_path, exist_ok=True)
        ConsoleUtility.print("--splitting pdf into images--")

        # open pdf and split it into rgb-pixel maps -> png
        doc = fitz.open(self.origin_path)
        for page in doc:
            ConsoleUtility.print(f"** - Finished Page {page.number + 1}/{len(doc)}")
            pix = page.get_pixmap(dpi=self.__dpi)
            page_number = str(page.number) if page.number >= 10 else "0" + str(page.number)
            pix.save(os.path.join(self.dest_path, 'page_%s.png' % page_number))
