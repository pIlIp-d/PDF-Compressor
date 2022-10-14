from PIL.Image import DecompressionBombError

from django_app.plugin_system.processing_classes.converter import Converter
from django_app.utility.console_utility import ConsoleUtility

# package name PyMuPdf
import fitz  # also imports convert() method

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


# TODO consoleUI processor


class ImagesToPdfConverter(Converter):

    # TODO to see supported formats run 'python3.10 -m PIL'. needed are 'save' and 'open'
    def __init__(
            self,
            pytesseract_path: str = None,
            force_ocr: bool = False,
            no_ocr: bool = False,
            tesseract_language: str = "deu",
            tessdata_prefix: str = "",
            event_handlers=None
    ):
        super().__init__(event_handlers, "", "pdf", True, True)
        if force_ocr and no_ocr:
            raise ValueError("force_ocr and no_ocr can't be used together")
        self.force_ocr = (force_ocr or not no_ocr) and PY_TESS_AVAILABLE and pytesseract_path is not None
        self.no_ocr = no_ocr
        self.tesseract_language = tesseract_language
        self.tessdata_prefix = rf"{tessdata_prefix}"
        self.pytesseract_path = pytesseract_path

        try:
            self.__init_pytesseract()
        except ValueError:
            self.force_ocr = False

    def __init_pytesseract(self) -> None:
        # either initiates pytesseract or deactivate ocr if not possible
        try:
            if not os.path.isfile(self.pytesseract_path):
                ConsoleUtility.print_error(r"[ ! ] - tesseract Path not found. Install "
                                           "https://github.com/UB-Mannheim/tesseract/wiki or edit "
                                           "'TESSERACT_PATH' to your specific tesseract executable")
                raise Exception()
            # set command (not sure why windows needs it differently)
            elif os.name == "nt":
                pytesseract.pytesseract.tesseract_cmd = f"{self.pytesseract_path}"
            else:
                pytesseract.tesseract_cmd = f"{self.pytesseract_path}"

        except Exception:
            if self.force_ocr:
                ConsoleUtility.print_error("Tesseract Not Loaded, Can't create OCR."
                                           "(leave out option '--ocr-force' to compress without ocr)")
                self.force_ocr = False
            raise ValueError("Tesseract (-> no OCR on pdfs)")

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        # merge page files into final destination
        merger = fitz.open()
        for file in file_list:
            if os.path.exists(merged_result_file):
                with fitz.open(merged_result_file) as f:
                    merger.insert_pdf(f)
            with fitz.open(file) as f:
                merger.insert_pdf(f)
            os.remove(file)
        merger.save(merged_result_file)
        # TODO move print to extra Processor
        # TODO maybe add event 'merged'
        ConsoleUtility.print("finished merge")

    def process_file(self, source_file: str, destination_file: str) -> None:
        # create destination directory if not already exists
        os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        try:
            if not self.force_ocr or self.no_ocr:
                raise ValueError("skipping tesseract")

            result = pytesseract.image_to_pdf_or_hocr(
                Image.open(source_file), lang=self.tesseract_language,
                extension="pdf",
                config=self.tessdata_prefix
            )
        except DecompressionBombError as e:
            raise e
        except ValueError:  # if ocr/tesseract fails or is skipped on purpose
            result = convert(source_file)
            ConsoleUtility.print_error("No OCR applied.")

        with open(destination_file, "wb") as f:
            f.write(result)
