#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================
import math
from types import SimpleNamespace

import jsons
import os
import shutil

from .console_ui_processor import ConsoleUIProcessor
from .io_path_parser import IOPathParser
from .compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from .compressor.pdf_crunch_compressor import PDFCrunchCompressor
from .utility.console_utility import ConsoleUtility
from .utility.os_utility import OsUtility


# TODO rename private variables starting with __ and protected starting with _


class PDFCompressor:

    def __init__(
            self,
            source_path: str,
            destination_path: str = "default",
            compression_mode: int = 3,  # TODO rename everywhere mode -> compression_mode
            continue_position: int = 0,
            force_ocr: bool = False,
            no_ocr: bool = False,
            quiet: bool = False,
            tesseract_language: str = "deu",
            simple_and_lossless: bool = False
    ):
        ConsoleUtility.QUIET_MODE = quiet
        self.__continue_position = continue_position  # todo reimplementation
        self.__force_ocr = force_ocr
        self.__simple_and_lossless = simple_and_lossless
        self.__final_merge_path = None
        self.__no_ocr = no_ocr
        self.__tesseract_language = tesseract_language
        self.__compression_mode = compression_mode

        self.__uses_default_destination = destination_path == "default"

        self.__source_path = rf"{os.path.abspath(source_path)}"
        self.__destination_path = destination_path if self.__uses_default_destination else rf"{os.path.abspath(destination_path)}"

        pdf_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
        os.chdir(pdf_dir)

        if not os.path.exists(self.__source_path):
            PDFCompressor.__raise_value_error(
                "option -p/--path must be a valid path to a file or folder."
            )
        if compression_mode < 1 or compression_mode > 10:
            PDFCompressor.__raise_value_error(
                "option -m/--mode must be in range 1 to 10."
            )
        if self.__force_ocr and no_ocr:
            PDFCompressor.__raise_value_error(
                "option -f/--force-ocr and -n/--no-ocr can't be used together"
            )

        # configure compressors
        config_paths = self.__get_config()

        # lossless compressor
        self.__cpdf = CPdfSqueezeCompressor(config_paths.cpdfsqueeze_path, True)
        if not self.__simple_and_lossless:
            # lossy compressor
            self.__pdf_crunch = self.__get_and_configure_pdf_crunch(config_paths, self.__cpdf)

    def __get_and_configure_pdf_crunch(self, config_paths, cpdf: CPdfSqueezeCompressor) -> PDFCrunchCompressor:
        pdf_crunch = PDFCrunchCompressor(config_paths.pngquant_path, config_paths.advpng_path, cpdf, self.__compression_mode)

        if not self.__no_ocr:  # TODO dependency unitTests
            pdf_crunch.enable_tesseract(
                config_paths.tesseract_path,
                self.__force_ocr,
                self.__no_ocr,
                self.__tesseract_language,
                config_paths.tessdata_prefix
            )
        return pdf_crunch

    @staticmethod
    def __get_config():
        config_path = os.path.abspath("./config.json")  # todo test if path works when not executed via __main__.py
        if not os.path.isfile(config_path):
            raise FileNotFoundError("config.json not found, set the proper paths and run config.py")

        class Config:
            def __init__(self, advpng_path, pngquant_path, cpdfsqueeze_path, tesseract_path, tessdata_prefix):
                self.advpng_path = advpng_path
                self.pngquant_path = pngquant_path
                self.cpdfsqueeze_path = cpdfsqueeze_path
                self.tesseract_path = tesseract_path
                self.tessdata_prefix = tessdata_prefix

        with open(config_path, "r") as config_file:
            obj = jsons.loads(config_file.read(), object_hook=lambda d: SimpleNamespace(**d))
        return Config(**obj)

    def __write_file_to_final_location(self, temp_path: str, final_destination: str) -> None:
        if temp_path == final_destination:
            return  # skip copy
        output_dir = os.path.dirname(final_destination)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        shutil.copy(temp_path, final_destination)
        os.remove(temp_path)

    def compress(self) -> None:
        """
        if math.fabs(self.__continue_position) >= len(self.__source_file_list):
            ConsoleUtility.print(ConsoleUtility.get_error_string(
                "Continue Position exceeds the amount of pdf-files in input folder."
            ))
            return
        """
        self.__pdf_crunch.add_processor(ConsoleUIProcessor())

        if self.__simple_and_lossless:
            self.__cpdf.compress(self.__source_path, self.__destination_path)
        else:
            self.__pdf_crunch.compress(self.__source_path, self.__destination_path)

    @staticmethod
    def __raise_value_error(error_string: str) -> None:
        ConsoleUtility.print(ConsoleUtility.get_error_string(error_string))
        raise ValueError(error_string)
