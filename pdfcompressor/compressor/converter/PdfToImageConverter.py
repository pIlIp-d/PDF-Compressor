from pdfcompressor.compressor.converter.Converter import *
from pdfcompressor.utility.ConsoleUtility import ConsoleUtility
from pdfcompressor.utility.OsUtility import OsUtility

import os

# package name PyMuPdf
import fitz


class PdfToImageConverter(Converter):
    def __init__(
            self,
            origin_path: str,
            dest_path: str,
            mode: int = 5
    ):
        super().__init__(origin_path, dest_path)
        self.mode = mode

    def convert(self) -> None:
        ConsoleUtility.print(self.dest_path)
        os.makedirs(self.dest_path, exist_ok=True)
        ConsoleUtility.print("--splitting pdf into images--")
        # open pdf and split it into rgb-pixelmaps -> png
        doc = fitz.open(self.origin_path)
        for page in doc:
            ConsoleUtility.print("** - {:.2f}%".format(100 * page.number / len(doc)))
            pix = page.get_pixmap(matrix=fitz.Matrix(self.mode, self.mode))
            pix.save(os.path.join(self.dest_path, 'page_%i.png' % page.number))
        ConsoleUtility.print("** - 100.00%")
