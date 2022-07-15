import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from pdfcompressor.compressor.converter.converter import Converter
from pdfcompressor.compressor.converter.convert_exception import ConvertException
from pdfcompressor.compressor.converter.py_tesseract_not_found_exception import PytesseractNotFoundException
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility

# package name PyMuPdf
import fitz  # also imports convert() method

import os
from PIL import Image
from img2pdf import convert

# OCR for pdf
try:
    import pytesseract

    PY_TESS_AVAILABLE = True
except:
    PY_TESS_AVAILABLE = False

# optionally add --tessdata 'path_to_tessdata_folder'
TESSDATA_PREFIX = ""


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
        self.tessdata_prefix = tessdata_prefix
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
            pytesseract.tesseract_cmd = self.pytesseract_path
        except Exception as ee:
            if self.force_ocr:
                ConsoleUtility.print(ConsoleUtility.get_error_string("Tesseract Not Loaded, Can't create OCR."
                                                                     "(leave out option '--ocr-force' to compresss without ocr)"))
                self.force_ocr = False
            raise ConvertException("Tesseract (-> no OCR on pdfs)")

    def convert(self) -> None:
        # merging pngs to pdf and create OCR
        ConsoleUtility.print("--merging compressed images into new pdf and creating OCR--")
        pdf = fitz.open()

        # convert single images in parallel
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            tasks = []
            for img, image_id in zip(self.images, range(len(self.images))):
                method_parameter = {"img_path": img, "page_id": image_id}
                # each image gets a single thread that which is executed via ThreadPoolExecutor
                tasks.append(executor.submit(self.convert_image_to_pdf, **method_parameter))

            # waits for all jobs to be completed
            for img in as_completed(tasks):
                pass

            for img in self.images:
                # merge pdfs
                with fitz.open(f"{img}.pdf") as f:
                    pdf.insert_pdf(f)

        if not os.path.isdir(os.path.sep.join(self.dest_path.split(os.path.sep)[:-1])) and not os.path.sep.join(
                self.dest_path.split(os.path.sep)[:-1]) == "":
            ConsoleUtility.print(self.dest_path.split(os.path.sep))
            os.mkdir(os.path.sep.join(self.dest_path.split(os.path.sep)[:-1]))
        ConsoleUtility.print("** - 100.00%")
        # raises exception if no matching permissions in output folder
        pdf.save(self.dest_path)

    def convert_image_to_pdf(self, img_path, page_id):
        try:
            if not self.force_ocr or self.no_ocr:
                raise InterruptedError("skipping tesseract")
            result = pytesseract.image_to_pdf_or_hocr(
                Image.open(img_path), lang=self.tesseract_language,
                extension="pdf",
                config=self.tessdata_prefix
            )
            with open(img_path + ".pdf", "wb") as f:
                f.write(result)
        except InterruptedError as e:  # if ocr/tesseract fails
            with open(img_path + ".pdf", "wb") as f:
                f.write(convert(img_path))
            ConsoleUtility.print(ConsoleUtility.get_error_string("No OCR applied."))
        # free storage by deleting png
        os.remove(img_path)
        # print statistics
        ConsoleUtility.print(f"** - Finished Page {page_id+1}/{len(self.images)}")
