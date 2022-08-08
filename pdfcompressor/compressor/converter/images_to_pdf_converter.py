from PIL.Image import DecompressionBombError

from pdfcompressor.compressor.converter.converter import Converter
from pdfcompressor.compressor.converter.convert_exception import ConvertException
from pdfcompressor.compressor.converter.py_tesseract_not_found_exception import PytesseractNotFoundException
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility

# package name PyMuPdf
import fitz  # also imports convert() method
from PyPDF4 import PdfFileMerger, PdfFileReader

import os
# package name pillow
from PIL import Image
from img2pdf import convert

# OCR for pdf
try:
    import pytesseract

    PY_TESS_AVAILABLE = True
except:
    PY_TESS_AVAILABLE = False


class ImagesToPdfConverter(Converter):
    pytesseract_path: str

    def __init__(
            self,
            origin_path: str,
            dest_path: str,
            pytesseract_path: str = None,
            force_ocr: bool = False,
            no_ocr: bool = False,
            tesseract_language: str = "deu",
            tessdata_prefix: str = ""
    ):
        super().__init__(origin_path, dest_path)
        self.images = OsUtility.get_file_list(origin_path, ".png")
        self.images.sort()
        if force_ocr and no_ocr:
            raise ValueError("force_ocr and no_ocr can't be used together")

        self.force_ocr = (force_ocr or not no_ocr) and PY_TESS_AVAILABLE
        self.no_ocr = no_ocr
        self.tesseract_language = tesseract_language
        self.tessdata_prefix = rf"{tessdata_prefix}"
        if pytesseract_path is not None:
            self.pytesseract_path = pytesseract_path
            try:
                self.init_pytesseract()
            except ConvertException as e:
                self.force_ocr = False

    def init_pytesseract(self) -> None:
        # either initiates pytesseract or deactivate ocr if not possible
        try:
            if not os.path.isfile(self.pytesseract_path):
                raise PytesseractNotFoundException()
            # set command (not sure why windows needs it differently)
            if os.name == "nt":
                pytesseract.pytesseract.tesseract_cmd = f"{self.pytesseract_path}"
            else:
                pytesseract.tesseract_cmd = f"{self.pytesseract_path}"

        except Exception as ee:
            if self.force_ocr:
                ConsoleUtility.print(ConsoleUtility.get_error_string("Tesseract Not Loaded, Can't create OCR."
                                                                     "(leave out option '--ocr-force' to compresss without ocr)"))
                self.force_ocr = False
            raise ConvertException("Tesseract (-> no OCR on pdfs)")

    def convert(self) -> None:
        # merging pngs to pdf and create OCR
        ConsoleUtility.print("--merging compressed images into new pdf and creating OCR--")
        # convert single images in parallel
        args_list = [{"img_path": img, "page_id": image_id} for img, image_id in zip(self.images, range(len(self.images)))]
        self._custom_map_execute(self.convert_image_to_pdf, args_list)

        # merge page files into final destination
        with fitz.open() as pdf:
            for file in self.images:
                pdf.insert_pdf(fitz.open(file + ".pdf"))
            pdf.save(self.dest_path)

    def convert_image_to_pdf(self, img_path, page_id):
        try:
            if not self.force_ocr or self.no_ocr:
                raise ValueError("skipping tesseract")

            result = pytesseract.image_to_pdf_or_hocr(
                Image.open(img_path), lang=self.tesseract_language,
                extension="pdf",
                config=self.tessdata_prefix
            )
            with open(img_path + ".pdf", "wb") as f:
                f.write(result)
        except DecompressionBombError as e:
            raise e
        except ValueError:  # if ocr/tesseract fails
            with open(img_path + ".pdf", "wb") as f:
                f.write(convert(img_path))
            ConsoleUtility.print(ConsoleUtility.get_error_string("No OCR applied."))
        # free storage by deleting png
        os.remove(img_path)
        # print statistics
        ConsoleUtility.print(f"** - Finished Page {page_id+1}/{len(self.images)}")
