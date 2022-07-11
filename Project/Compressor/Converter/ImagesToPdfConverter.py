from Project.Compressor.Converter.Converter import Converter
from Project.Compressor.Converter.ConvertException import ConvertException
from Project.Compressor.Converter.PyTesseractNotFoundException import PytesseractNotFoundException
from Project.Utility.ConsoleUtility import ConsoleUtility
from Project.Utility.OsUtility import OsUtility

# package name PyMuPdf
import fitz

import os
from PIL import Image
from img2pdf import convert

# OCR for pdf
try:
    import pytesseract
except:
    PY_TESS_AVAILABLE = False
else:
    PY_TESS_AVAILABLE = True

# optional add --tessdata 'path_to_tessdata_folder'
TESSDATA_PREFIX = ""


class ImagesToPdfConverter(Converter):
    pytesseract_path: str

    def __init__(self, origin_path: str, dest_path: str, pytesseract_path: str = None, force_ocr: bool = False):
        super().__init__(origin_path, dest_path)
        self.images = OsUtility.get_file_list(origin_path, ".png")
        self.force_ocr = force_ocr and PY_TESS_AVAILABLE
        if pytesseract_path is not None:
            self.pytesseract_path = pytesseract_path
            try:
                self.init_pytesseract()
            except ConvertException as e:
                print(str(e))
                self.force_ocr = False

    def init_pytesseract(self):
        # either initiates pytesseract or deactivate ocr if not possible
        try:
            if not os.path.isfile(self.pytesseract_path):
                raise PytesseractNotFoundException()
            pytesseract.tesseract_cmd = self.pytesseract_path
        except Exception as ee:
            print(ee)
            if self.force_ocr:
                ConsoleUtility.print(ConsoleUtility.get_error_string("Tesseract Not Loaded, Can't create OCR."
                                                      "(leave out option '--ocr-force' to compresss without ocr)"))
                self.force_ocr = False
                return False
            raise ConvertException("Tesseract (-> no OCR on pdfs)")
        return True

    def convert(self):
        # merging pngs to pdf and create OCR
        ConsoleUtility.print("--merging compressed images into new pdf and creating OCR--")
        pdf = fitz.open()
        i = 0
        for img in self.images:
            ConsoleUtility.print("** - {:.2f}%".format(100 * i / len(self.images)))
            i += 1
            try:
                if not self.force_ocr:
                    raise Exception("skipping tesseract")
                result = pytesseract.image_to_pdf_or_hocr(Image.open(img), lang="deu", extension="pdf",
                                                          config=TESSDATA_PREFIX)
                with open(img + ".pdf", "wb") as f:
                    f.write(result)
            except Exception:  # if ocr/tesseract fails
                with open(img + ".pdf", "wb") as f:
                    f.write(convert(img))
                if self.force_ocr:
                    ConsoleUtility.print(ConsoleUtility.get_error_string("OCR couldn't be processed."))
                # ignore if ocr cant be done
            with fitz.open(img + ".pdf") as f:
                pdf.insert_pdf(f)
        if not os.path.isdir(os.path.sep.join(self.dest_path.split(os.path.sep)[:-1])) and not os.path.sep.join(
                self.dest_path.split(os.path.sep)[:-1]) == "":
            ConsoleUtility.print(self.dest_path.split(os.path.sep))
            os.mkdir(os.path.sep.join(self.dest_path.split(os.path.sep)[:-1]))
        ConsoleUtility.print("** - 100.00%")
        # raises exception if no matching permissions in output folder
        pdf.save(self.dest_path)
