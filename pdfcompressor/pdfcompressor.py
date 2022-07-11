#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================
import os
import shutil

from compressor.CPdfSqeezeCompressor import CPdfSqueezeCompressor
from compressor.CrunchCompressor import CrunchCompressor
from utility.ConsoleUtility import ConsoleUtility
from utility.OsUtility import OsUtility

global PNGQUANT_PATH, ADVPNG_PATH, CPDFSQUEEZE_PATH, TESSERACT_PATH


class PDFCompressor:
    def __init__(
            self,
            source_path: str,
            destination_path: str,
            mode: int,
            continue_position: int = 0,
            force_ocr: bool = False,
            no_ocr: bool = False,
            quiet: bool = False,
            tesseract_language: str = "deu"
    ):
        ConsoleUtility.QUIET_MODE = quiet

        if not os.path.exists(source_path):
            PDFCompressor.__raise_value_error(
                "option -p/--path must be a valid path to a file or folder."
            )
        if not os.path.exists(destination_path):
            PDFCompressor.__raise_value_error(
                "option -o/--output-path must be a valid path to a file or folder."
            )
        if mode < 1 or mode > 10:
            PDFCompressor.__raise_value_error(
                "option -m/--mode must be in range 1 to 10."
            )
        if continue_position < 0:
            PDFCompressor.__raise_value_error(
                "option -c/--continue must be greater than or equals to 0"
            )
        if force_ocr and no_ocr:
            PDFCompressor.__raise_value_error(
                "option -s/--force-ocr and -n/--no-ocr can't be used together"
            )

        self.source_path = rf"{os.path.abspath(source_path)}"
        self.destination_path = rf"{os.path.abspath(destination_path)}"
        self.__parse_paths()

        self.mode = mode
        self.continue_position = continue_position
        self.force_ocr = force_ocr
        self.no_ocr = no_ocr
        self.tesseract_language = tesseract_language
        self.source_file_list = []
        self.destination_file_list = []

        # save size for comparison
        self.orig_size = os.stat(self.source_path).st_size

        # lossy compressor
        self.crunch = CrunchCompressor(self.mode, PNGQUANT_PATH, ADVPNG_PATH)
        self.crunch.enable_tesseract(TESSERACT_PATH, self.force_ocr, self.no_ocr, self.tesseract_language)
        # lossless compressor
        self.cpdf = CPdfSqueezeCompressor(CPDFSQUEEZE_PATH, True)

        self.compress_file_list()

    def __parse_paths(self) -> None:
        # fills file_list with all pdf files that are going to be compressed
        # source_path is a folder -> len(file_list) >= 0 depending on how many files are found
        if os.path.isdir(self.source_path):
            if os.path.isfile(self.destination_path):
                raise ValueError(
                    "OptionError: If path is a directory the output_path must be one too!"
                )  # TODO make a merge possible

            elif self.destination_path == "default":
                self.destination_path = os.path.abspath(self.source_path) + "_compressed"

            self.source_file_list = OsUtility.get_file_list(self.source_path, ".pdf")

            for file in self.source_file_list:
                self.destination_file_list.append(
                    rf"{self.destination_path}/{OsUtility.get_filename(file)}_compressed.pdf")

        # source_path is a file -> len(file_list) == 1
        else:
            if self.destination_path == "default":
                self.destination_path = os.path.abspath(self.source_path[:-4]) + "_compressed.pdf"

            elif not os.path.isfile(self.destination_path):
                self.destination_path = os.path.join(
                    self.destination_path,
                    self.source_path.split(os.path.sep)[-1]
                )
            self.source_file_list.append(self.source_path)
            self.destination_file_list.append(self.destination_path)

        # the two list should have the same length
        assert len(self.destination_file_list) == len(self.source_file_list)
        if len(self.source_file_list):
            self.__raise_value_error(f"Found no Pdf at -p/--path {self.source_path}")

    def compress_file_list(self) -> None:
        for file, destination in self.source_file_list, self.destination_file_list:
            ConsoleUtility.print("compressing " + ConsoleUtility.get_file_string(file))

            # compress
            self.crunch.compress(file, destination)
            self.cpdf.compress(destination, destination)

            # if not force_ocr check if compression was successful
            size_after_compression = os.stat(destination).st_size
            if not self.force_ocr and self.orig_size < size_after_compression:
                # try compressing only with cpdf
                self.cpdf.compress(file, destination)
                cpdf_compression_only_size = os.stat(destination).st_size
                if self.orig_size < cpdf_compression_only_size:
                    shutil.copy(file, destination)
                else:
                    ConsoleUtility.print(ConsoleUtility.get_error_string("File couldn't be compressed."))
                ConsoleUtility.print(ConsoleUtility.get_error_string("No OCR created."))

            ConsoleUtility.print_stats(self.orig_size, os.stat(destination).st_size)
            ConsoleUtility.print("created " + ConsoleUtility.get_file_string(destination))

    @staticmethod
    def __raise_value_error(error_string: str) -> None:
        ConsoleUtility.print(ConsoleUtility.get_error_string(error_string))
        raise ValueError(error_string)