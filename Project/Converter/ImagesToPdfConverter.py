import os

# package name PyMuPdf
import fitz
from PIL import Image
from img2pdf import convert

from Project.Converter.Converter import Converter
from Project.Converter.ConvertException import ConvertException
from Project.Converter.PyTesseractNotFoundException import PytesseractNotFoundException
from Project.Utility.OsUtility import OsUtility

# OCR for pdf
try:
    import pytesseract
except:
    PY_TESS_AVAILABLE = False
else:
    PY_TESS_AVAILABLE = True


class ImagesToPdfConverter(Converter):
    pytesseract_path: str

    def __init__(self, origin_path, dest_path, mode=5, pytesseract_path=None, force_ocr=False):
        super().__init__(origin_path, dest_path)
        self.images = OsUtility.get_file_list(origin_path, ".png")
        self.mode = mode
        self.force_ocr = force_ocr and PY_TESS_AVAILABLE
        if pytesseract_path is not None:
            self.pytesseract_path = pytesseract_path
            try:
                self.init_pytesseract()
            except ConvertException as e:
                print(str(e))
                pytesseract_path = None
                force_ocr = False

    def init_pytesseract(self): # TODO
        global TESSERACT_PATH, TESSDATA_PREFIX
        # pytesseract setup
        TESSERACT_PATH = self.pytesseract_path
        try:
            if self.pytesseract_path is not None:
                self.pytesseract_path = os.path.join(os.path.expanduser('~'),
                                                     "AppData", "Local", "Programs", "Tesseract-OCR", "tesseract.exe")
            TESSDATA_PREFIX = "--tessdata-dir '" + os.path.join(
                            os.path.expanduser('~'), "AppData", "Local", "Programs", "Tesseract-OCR", "tessdata") + "'"
            if not os.path.isfile(TESSERACT_PATH):
                raise PytesseractNotFoundException()
                quit(5)  # TODO documentation

            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        except:
            if self.force_ocr:
                print("Tesseract Not Loaded, Can't create OCR."
                      "(leave out option '--ocr-force' to compresss without ocr)")
                self.force_ocr = False
                return False
            raise ConvertException("Tesseract (-> no OCR on pdfs)")
        return True

    def convert(self):
        # merging pngs to pdf and create OCR
        print("--merging compressed images into new pdf and creating OCR--")
        pdf = fitz.open()
        i = 0
        for img in self.images:
            print("** - {:.2f}%".format(100 * i / len(self.images)))
            i += 1
            try:
                if not self.force_ocr:
                    raise Exception("skipping tesseract")
                result = pytesseract.image_to_pdf_or_hocr(Image.open(img), lang="deu", extension="pdf",
                                                          config=TESSDATA_PREFIX)
                open(img + ".pdf", "wb").write(result)
            except:  # if ocr/tesseract fails
                with open(img + ".pdf", "wb") as f:
                    f.write(convert(img))
                if self.force_ocr:
                    print("OCR couldn't be processed.")
                # ignore if ocr cant be done
            pdf.insert_pdf(fitz.open(img + ".pdf"))
        if not os.path.isdir(os.path.sep.join(self.dest_path.split(os.path.sep)[:-1])) and not os.path.sep.join(
                self.dest_path.split(os.path.sep)[:-1]) == "":
            print(self.dest_path.split(os.path.sep))
            os.mkdir(os.path.sep.join(self.dest_path.split(os.path.sep)[:-1]))
        print("** - 100.00%")
        # raises exception if no matching permissions in output folder
        pdf.save(self.dest_path)
