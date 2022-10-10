#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================

import os
from enum import Enum

from .compressor.pdf_compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from .compressor.pdf_compressor.pdf_crunch_compressor import PDFCrunchCompressor
from .utility import EventHandler
from .utility.console_utility import ConsoleUtility
from .utility.os_utility import OsUtility


class PdfCompressorOptionHelp(Enum):
    source_path = ""
    destination_path = ""
    force_ocr = ""
    no_ocr = ""
    quiet = ""
    tesseract_language = ""
    simple_and_lossless = ""
    default_pdf_dpi = ""
    event_handlers = ""


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
            event_handlers: list[EventHandler] = list()
    ):
        ConsoleUtility.quiet_mode = quiet
        self.__force_ocr = force_ocr
        self.__simple_and_lossless = simple_and_lossless
        self.__final_merge_path = None
        self.__no_ocr = no_ocr
        self.__tesseract_language = tesseract_language
        self.__compression_mode = compression_mode
        self.__default_pdf_dpi = default_pdf_dpi
        self.__event_handlers = event_handlers
        self.__uses_default_destination = destination_path == "default"

        self.__source_path = rf"{os.path.abspath(source_path)}"
        self.__destination_path = \
            destination_path if self.__uses_default_destination else rf"{os.path.abspath(destination_path)}"

        pdf_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
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
        try:
            self.__cpdf = CPdfSqueezeCompressor(
                config_paths.cpdfsqueeze_path,
                config_paths.wine_path,
                event_handlers=event_handlers if self.__simple_and_lossless else list()
            )
        except ValueError:
            ConsoleUtility.print_error("Error: Program cpdfsqueeze not found or configured inorrectly, "
                                       "skipped compression with cpdfsqueeze.")
            self.__cpdf = None
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
            self.__default_pdf_dpi,
            self.__event_handlers
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

    def compress(self) -> None:
        for event_handler in self.__event_handlers:
            event_handler.started_processing()
        if self.__simple_and_lossless:
            self.__cpdf.compress(self.__source_path, self.__destination_path)
        else:
            self.__pdf_crunch.compress(self.__source_path, self.__destination_path)
        for event_handler in self.__event_handlers:
            event_handler.finished_all_files()

    @staticmethod
    def __raise_value_error(error_string: str) -> None:
        ConsoleUtility.print(ConsoleUtility.get_error_string(error_string))
        raise ValueError(error_string)

# TODO consider adding conversion from png to jpeg before the merge if no alpha is needed
