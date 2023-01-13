import os
import shutil
import sys
from enum import Enum
from io import TextIOWrapper

from django_app.plugin_system.processing_classes.event_handler import EventHandler
from plugins.crunch_compressor.converter.images_to_pdf_converter import ImagesToPdfConverter
from plugins.crunch_compressor.converter.pdf_to_image_converter import PdfToImageConverter
from django_app.plugin_system.processing_classes.abstract_pdf_compressor import AbstractPdfProcessor
from plugins.crunch_compressor.compressor.pdf_compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from plugins.crunch_compressor.compressor.png_compressor.png_crunch_compressor import PNGCrunchCompressor
from plugins.crunch_compressor.config import get_config


class PDFCrunchCompressor(AbstractPdfProcessor):
    Mode = Enum("Mode", ["AUTO", "LOSSLESS", "FORCE_OCR", "NO_OCR"])

    def __init__(
            self,
            compression_mode: int = 5,
            force_ocr: bool = False,
            no_ocr: bool = False,
            tesseract_language: str = "eng",
            simple_and_lossless: bool = False,
            default_pdf_dpi: int = 400,
            event_handlers: list[EventHandler] = None
    ):
        if event_handlers is None:
            event_handlers = list()
        super().__init__(event_handlers, True)
        self.__tessdata_prefix = None
        self.__force_ocr = force_ocr
        self.__simple_and_lossless = simple_and_lossless

        # configure compressors
        config_paths = get_config()
        try:
            # lossless compressor
            self.__cpdf_squeeze_compressor = CPdfSqueezeCompressor(
                config_paths.cpdfsqueeze_path,
                config_paths.wine_path,
                event_handlers=event_handlers if simple_and_lossless else list()
            )
        except ValueError as error:
            self.__cpdf_squeeze_compressor = None
            if simple_and_lossless:
                raise ValueError("when forcing cpdf with simple_and_lossless the cpdf path must be valid!")
            else:
                print(str(error) + " -> skipping compression with cpdfsqueeze.")

        tesseract_path = None
        if not simple_and_lossless:
            if not no_ocr:
                # enable tesseract
                if os.path.exists(config_paths.tesseract_path):
                    tesseract_path = config_paths.tesseract_path
                else:
                    if force_ocr:
                        raise ValueError(
                            "tesseract_path not found."
                            "If force-ocr is active tesseract needs to be configured correctly."
                        )
        # init lossy compressor
        self.__png_crunch_compressor = PNGCrunchCompressor(
            config_paths.pngquant_path,
            config_paths.advpng_path,
            config_paths.pngcrush_path,
            compression_mode
        )
        self.__image_to_pdf_converter = ImagesToPdfConverter(
            tesseract_path,
            self.__force_ocr,
            no_ocr,
            tesseract_language,
            config_paths.tessdata_prefix
        )
        self.__pdf_to_image_converter = PdfToImageConverter("png", default_pdf_dpi)

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
        return os.path.abspath(os.path.join("temporary_files", cls._get_filename(file).replace(" ", "_") + "_tmp"))

    def __custom_preprocess(self, source_file: str, destination_file: str, temp_folder: str) -> None:
        super().preprocess(source_file, destination_file)

        # create new empty folder for temporary files
        shutil.rmtree(temp_folder, ignore_errors=True)
        os.makedirs(temp_folder)

        # split pdf into images that can be compressed using crunch
        self.__pdf_to_image_converter.process(source_file, temp_folder)

    def __custom_postprocess(self, source_file: str, destination_file: str, temp_folder: str) -> None:
        # merge images/pages into new pdf and optionally apply OCR
        self.__image_to_pdf_converter.process(temp_folder, destination_file)
        shutil.rmtree(temp_folder, ignore_errors=True)
        # supress normal console outputs
        stdin_buffer = sys.stdin
        sys.stdin = TextIOWrapper(open(os.devnull, "w"))

        if self.__cpdf_squeeze_compressor is not None:
            # compression with cpdf
            self.__cpdf_squeeze_compressor.process(destination_file, destination_file)

        if not self.__force_ocr and self._get_file_size(source_file) < self._get_file_size(destination_file):
            if self.__cpdf_squeeze_compressor is not None:
                self.__cpdf_squeeze_compressor.process_file(source_file, destination_file)
            if self._get_file_size(source_file) < self._get_file_size(destination_file):
                print("File couldn't be compressed.", file=sys.stderr)
                # copy source_file to destination_file
                if not source_file == destination_file:
                    shutil.copy(source_file, destination_file)
            else:
                print(
                    "File couldn't be compressed using crunch cpdf combi. "
                    "However cpdf could compress it. -> No OCR was Created. (force ocr with option -f/--force-ocr)"
                    , file=sys.stderr
                )
        # load normal stdin from buffer
        sys.stdin = stdin_buffer
        super().postprocess(source_file, destination_file)

    def process(self, source_path, destination_path="default"):
        if self.__simple_and_lossless:
            self.__cpdf_squeeze_compressor.process(source_path, destination_path)
        else:
            super().process(source_path, destination_path)

    def process_file(self, source_file: str, destination_path: str) -> None:
        temp_folder = self._get_and_create_temp_folder()
        self.__custom_preprocess(source_file, destination_path, temp_folder)

        # compress all images in temp_folder
        self.__png_crunch_compressor.process(temp_folder, temp_folder)
        self.__custom_postprocess(source_file, destination_path, temp_folder)
