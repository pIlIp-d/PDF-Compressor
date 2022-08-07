import os
import shutil

from .abstract_pdf_compressor import AbstractPdfCompressor
from .converter.images_to_pdf_converter import ImagesToPdfConverter
from .converter.pdf_to_image_converter import PdfToImageConverter
from .cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from .crunch_utility import CrunchUtility
from .processor import Processor
from ..utility.console_utility import ConsoleUtility
from ..utility.os_utility import OsUtility


class PDFCrunchCompressor(AbstractPdfCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            c_pdf_squeeze_compressor: CPdfSqueezeCompressor,
            compressing_mode: int,
            processor: Processor = None
    ):
        super().__init__(processor)
        self.__crunch_utility = CrunchUtility(pngquant_path, advpng_path)
        self.__tessdata_prefix = None
        self.__tesseract_path = None
        self.__tesseract_language = None
        self.__force_ocr = False
        self.__no_ocr = True
        self.__c_pdf_squeeze_compressor = c_pdf_squeeze_compressor
        self.__compressing_mode = compressing_mode
        if self.__compressing_mode <= 0 or self.__compressing_mode >= 11:
            raise ValueError("Mode must be between 1 and 10")

    def enable_tesseract(
            self,
            tesseract_path: str,
            force_ocr: bool = False,
            no_ocr: bool = False,
            tesseract_language: str = "deu",
            tessdata_prefix: str = ""
    ) -> None:

        if not os.path.exists(tesseract_path):
            if force_ocr:
                raise ValueError(
                    "tesseract_path not found. If force-ocr is active tesseract needs to be configured correctly.")
            else:
                tesseract_path = None
        self.__tesseract_path = tesseract_path
        self.__force_ocr = force_ocr
        self.__no_ocr = no_ocr
        self.__tesseract_language = tesseract_language
        self.__tessdata_prefix = tessdata_prefix

    @staticmethod
    def __get_temp_path(file: str):
        # spaces are replaced because crunch can't handle spaces consistently
        return os.path.abspath(OsUtility.get_filename(file).replace(" ", "_") + "_tmp")

    def preprocess(self, source_file: str, destination_file: str) -> None:
        temp_folder = self.__get_temp_path(source_file)
        super().preprocess(source_file, destination_file)

        # create new empty folder for temporary files
        shutil.rmtree(temp_folder, ignore_errors=True)
        os.makedirs(temp_folder)

        # split pdf into images that can be compressed using crunch
        PdfToImageConverter(source_file, temp_folder, self.__compressing_mode).convert()

    def postprocess(self, source_file: str, destination_file: str) -> None:
        temp_folder = self.__get_temp_path(source_file)

        if destination_file.endswith(".pdf"):
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        else:
            os.makedirs(destination_file, exist_ok=True)

        # merge images/pages into new pdf and optionally apply OCR
        ImagesToPdfConverter(
            temp_folder,
            destination_file,
            self.__tesseract_path,
            self.__force_ocr,
            self.__no_ocr,
            self.__tesseract_language,
            self.__tessdata_prefix
        ).convert()
        OsUtility.clean_up_folder(temp_folder)

        self.__c_pdf_squeeze_compressor.supress_stats()
        self.__c_pdf_squeeze_compressor.compress(destination_file, destination_file)

        if not self.__force_ocr and OsUtility.get_file_size(source_file) < OsUtility.get_file_size(destination_file):
            self.__c_pdf_squeeze_compressor.compress_file(source_file, destination_file)
            if OsUtility.get_file_size(source_file) < OsUtility.get_file_size(destination_file):
                ConsoleUtility.print(ConsoleUtility.get_error_string("File couldn't be compressed."))
                # copy source_file to destination_file
                if not source_file == destination_file:
                    shutil.copy(source_file, destination_file)
            else:
                ConsoleUtility.print(ConsoleUtility.get_error_string(
                    "File couldn't be compressed using crunch cpdf combi. "
                    "However cpdf could compress it. -> No OCR was Created. (force ocr with option -f/--force-ocr)"
                ))
        self.__c_pdf_squeeze_compressor.activate_stats()

        super().postprocess(source_file, destination_file)

    def compress_file(self, file: str, _: str):
        # list of pdf pages in png format
        image_list = OsUtility.get_file_list(self.__get_temp_path(file), ".png")
        self.__crunch_utility.crunch_list_of_files(image_list)
