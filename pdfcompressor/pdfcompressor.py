#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================

import os

from .compressor.pdf_compressor.abstract_pdf_compressor import AbstractPdfCompressor
from .processor.console_ui_processor import ConsoleUIProcessor
from .compressor.pdf_compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from .compressor.pdf_compressor.pdf_crunch_compressor import PDFCrunchCompressor
from .processor.postprocessor import Postprocessor
from .processor.preprocessor import Preprocessor
from .utility.console_utility import ConsoleUtility

from .utility.os_utility import OsUtility


# TODO using **kwargs, read-only, password


class PDFCompressor:

    def __init__(
            self,
            source_path: str,
            destination_path: str = "default",
            compression_mode: int = 5,
            force_ocr: bool = False,
            no_ocr: bool = False,
            quiet: bool = False,
            tesseract_language: str = "deu",
            simple_and_lossless: bool = False,
            default_pdf_dpi: int = 400,
            extra_preprocessors: list[Preprocessor] = None,
            extra_postprocessors: list[Postprocessor] = None
    ):
        ConsoleUtility.quiet_mode = quiet
        self.__force_ocr = force_ocr
        self.__simple_and_lossless = simple_and_lossless
        self.__final_merge_path = None
        self.__no_ocr = no_ocr
        self.__tesseract_language = tesseract_language
        self.__compression_mode = compression_mode
        self.__default_pdf_dpi = default_pdf_dpi
        self.__extra_preprocessors = extra_preprocessors
        self.__extra_postprocessors = extra_postprocessors
        self.__uses_default_destination = destination_path == "default"

        self.__source_path = rf"{os.path.abspath(source_path)}"
        self.__destination_path = \
            destination_path if self.__uses_default_destination else rf"{os.path.abspath(destination_path)}"

        pdf_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
        os.chdir(pdf_dir)

        if not os.path.exists(self.__source_path):
            PDFCompressor.__raise_value_error(
                "option -p/--path must be a valid path to a file or folder."
            )
        if compression_mode < 1 or compression_mode > 5:
            PDFCompressor.__raise_value_error(
                "option -m/--mode must be in range 1 to 5."
            )
        if self.__force_ocr and no_ocr:
            PDFCompressor.__raise_value_error(
                "option -f/--force-ocr and -n/--no-ocr can't be used together"
            )

        # configure compressors
        config_paths = OsUtility.get_config()

        # lossless compressor
        self.__cpdf = CPdfSqueezeCompressor(config_paths.cpdfsqueeze_path, True)
        if not self.__simple_and_lossless:
            # lossy compressor
            self.__pdf_crunch = self.__get_and_configure_pdf_crunch(config_paths, self.__cpdf)

    def __get_and_configure_pdf_crunch(self, config_paths, cpdf: CPdfSqueezeCompressor) -> PDFCrunchCompressor:
        pdf_crunch = PDFCrunchCompressor(
            config_paths.pngquant_path,
            config_paths.advpng_path,
            config_paths.pngcrush_path,
            cpdf,
            self.__compression_mode,
            self.__default_pdf_dpi
        )

        if not self.__no_ocr:
            pdf_crunch.enable_tesseract(
                config_paths.tesseract_path,
                self.__force_ocr,
                self.__no_ocr,
                self.__tesseract_language,
                config_paths.tessdata_prefix
            )
        return pdf_crunch

    def __add_processors(self, compressor: AbstractPdfCompressor):
        console_ui_processor = ConsoleUIProcessor()
        compressor.add_postprocessor(console_ui_processor)
        for processor in self.__extra_preprocessors:
            compressor.add_preprocessor(processor)
        for processor in self.__extra_postprocessors:
            compressor.add_postprocessor(processor)

    def compress(self) -> None:
        if self.__simple_and_lossless:
            self.__add_processors(self.__cpdf)
            self.__cpdf.compress(self.__source_path, self.__destination_path)
        else:
            self.__add_processors(self.__pdf_crunch)
            self.__pdf_crunch.compress(self.__source_path, self.__destination_path)

    @staticmethod
    def __raise_value_error(error_string: str) -> None:
        ConsoleUtility.print(ConsoleUtility.get_error_string(error_string))
        raise ValueError(error_string)

# TODO consider adding conversion from png to jpeg before the merge if no alpha is needed
