import os
import shutil

from pdfcompressor.compressor.converter.images_to_pdf_converter import ImagesToPdfConverter
from pdfcompressor.compressor.converter.pdf_to_image_converter import PdfToImageConverter
from pdfcompressor.compressor.pdf_compressor.abstract_pdf_compressor import AbstractPdfCompressor
from pdfcompressor.compressor.pdf_compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from pdfcompressor.compressor.png_compressor.png_crunch_compressor import PNGCrunchCompressor
from pdfcompressor.processor.processor import Processor
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility


class PDFCrunchCompressor(AbstractPdfCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            c_pdf_squeeze_compressor: CPdfSqueezeCompressor,
            compressing_mode: int,
    ):
        super().__init__()
        self.__png_crunch_compressor = PNGCrunchCompressor(pngquant_path, advpng_path)
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
        super().preprocess(source_file, destination_file)
        temp_folder = self.__get_temp_path(source_file)

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

        ConsoleUtility.quiet_mode = True
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
        ConsoleUtility.quiet_mode = False
        super().postprocess(source_file, destination_file)

    def compress_file_list(self, source_files: list, destination_files: list) -> None:
        # todo compare results with parallel
        # don't use parallel pdf compression
        # instead it uses parallel image compression per
        for source, destination in zip(source_files, destination_files):
            self.compress_file(source, destination)

    @Processor.pre_and_post_processed
    def compress_file(self, source_file: str, destination_file: str) -> None:
        # compress all images in temp_folder
        temp_image_list = OsUtility.get_file_list(self.__get_temp_path(source_file))
        self.__png_crunch_compressor.compress_file_list(temp_image_list, temp_image_list)
