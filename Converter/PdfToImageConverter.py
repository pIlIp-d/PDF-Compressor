from Converter import *
import os

# package name PyMuPdf
import fitz


class PdfToImageConverter(Converter):
    def __init__(self, origin_path, dest_path, mode=5, os_type=0):
        super().__init__(origin_path, dest_path)
        self.mode = mode

    def convert(self):
        print("--splitting pdf into images--")
        # open pdf and split it into rgb-pixelmaps -> png
        doc = fitz.open(self.origin_path)
        for page in doc:
            print("** - {:.2f}%".format(100 * page.number / len(doc)))
            pix = page.get_pixmap(matrix=fitz.Matrix(self.mode, self.mode))
            pix.save(os.path.join(self.dest_path, 'page_%i.png' % page.number))
        print("** - 100.00%")