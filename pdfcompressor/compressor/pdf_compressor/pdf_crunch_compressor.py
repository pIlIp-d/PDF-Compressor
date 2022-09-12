import os
import shutil

from pdfcompressor.compressor.converter.images_to_pdf_converter import ImagesToPdfConverter
from pdfcompressor.compressor.converter.pdf_to_image_converter import PdfToImageConverter
from pdfcompressor.compressor.pdf_compressor.abstract_pdf_compressor import AbstractPdfCompressor
from pdfcompressor.compressor.pdf_compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from pdfcompressor.compressor.png_compressor.png_crunch_compressor import PNGCrunchCompressor
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility


class PDFCrunchCompressor(AbstractPdfCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            pngcrush_path: str,
            cpdf_squeeze_compressor: CPdfSqueezeCompressor,
            compression_mode: int,
            default_pdf_dpi: int = 400
    ):
        super().__init__()
        self.__png_crunch_compressor = PNGCrunchCompressor(pngquant_path, advpng_path, pngcrush_path, compression_mode)
        self.__tessdata_prefix = None
        self.__tesseract_path = None
        self.__tesseract_language = None
        self.__force_ocr = False
        self.__no_ocr = True
        self.__cpdf_squeeze_compressor = cpdf_squeeze_compressor
        if default_pdf_dpi < 0:
            raise ValueError("default dpi needs to be greater than 0")
        self.__default_pdf_dpi = default_pdf_dpi

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

    @classmethod
    def __get_new_temp_path(cls, file: str) -> str:
        temp_path = cls.__get_temp_path(file)
        if os.path.exists(temp_path):
            temp_path_prefix_and_number = temp_path.split("_tmp")
            temp_path_number = temp_path_prefix_and_number[-1] if temp_path_prefix_and_number[-1].isnumeric() else 0
            return "".join(temp_path_prefix_and_number[:-1]) + "_tmp" + str(int(temp_path_number) + 1)
        return temp_path

    @classmethod
    def __get_temp_path(cls, file: str) -> str:
        # spaces are replaced because crunch can't handle spaces consistently
        return os.path.abspath(os.path.join("temporary_files", OsUtility.get_filename(file).replace(" ", "_") + "_tmp"))

    def __custom_preprocess(self, source_file: str, destination_file: str, temp_folder: str) -> None:
        super().preprocess(source_file, destination_file)

        # create new empty folder for temporary files
        shutil.rmtree(temp_folder, ignore_errors=True)
        os.makedirs(temp_folder)

        # split pdf into images that can be compressed using crunch
        PdfToImageConverter(source_file, temp_folder, self.__default_pdf_dpi).convert()

    def __custom_postprocess(self, source_file: str, destination_file: str, temp_folder: str) -> None:
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

        # console output control and finishing compression
        quiet_mode_buffer = ConsoleUtility.quiet_mode
        # supress normal cpdf outputs
        ConsoleUtility.quiet_mode = True
        if self.__cpdf_squeeze_compressor is not None:
            show_errors_buffer = ConsoleUtility.show_errors_always
            if not quiet_mode_buffer:
                ConsoleUtility.show_errors_always = True
            # compression with cpdf
            self.__cpdf_squeeze_compressor.compress(destination_file, destination_file)
            ConsoleUtility.show_errors_always = show_errors_buffer

        if not self.__force_ocr and OsUtility.get_file_size(source_file) < OsUtility.get_file_size(destination_file):
            if self.__cpdf_squeeze_compressor is not None:
                self.__cpdf_squeeze_compressor.compress_file(source_file, destination_file)
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
        ConsoleUtility.quiet_mode = quiet_mode_buffer
        super().postprocess(source_file, destination_file)

    def compress_file_list(self, source_files: list, destination_files: list) -> None:
        # only use parallel compression of files, when there are more than 8 threads available
        if os.cpu_count() > 8:
            self.compress_file_list_multi_threaded(source_files, destination_files, os.cpu_count() // 4)
        else:
            # instead it uses parallel image compression per pdf
            for source, destination in zip(source_files, destination_files):
                self.compress_file(source, destination)

    def compress_file(self, source_file: str, destination_file: str) -> None:
        temp_folder = self.__get_new_temp_path(source_file)
        self.__custom_preprocess(source_file, destination_file, temp_folder)

        # compress all images in temp_folder
        self.__png_crunch_compressor.compress(temp_folder, temp_folder)
        self.__custom_postprocess(source_file, destination_file, temp_folder)
