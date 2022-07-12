#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================
import jsons
import os
import shutil

from .compressor.crunch_compressor import CrunchCompressor
from .compressor.cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from .utility.console_utility import ConsoleUtility
from .utility.os_utility import OsUtility


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

        print(source_path)
        source_path = os.path.abspath(source_path)
        print(source_path)
        if not os.path.exists(source_path):
            PDFCompressor.__raise_value_error(
                "option -p/--path must be a valid path to a file or folder."
            )
        # if not os.path.exists(destination_path):
        #     PDFCompressor.__raise_value_error(
        #         "option -o/--output-path must be a valid path to a file or folder."
        #     )
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

        self.uses_default_destination = destination_path == "default"

        self.source_path = rf"{os.path.abspath(source_path)}"
        self.destination_path = rf"{os.path.abspath(destination_path)}"
        self.source_file_list = []
        self.destination_file_list = []
        self.__parse_paths()

        self.mode = mode
        self.continue_position = continue_position
        self.force_ocr = force_ocr
        self.no_ocr = no_ocr
        self.tesseract_language = tesseract_language

        pngquant_path, advpng_path, cpdfsqueeze_path, tesseract_path = self.get_config()

        # lossy compressor
        self.crunch = CrunchCompressor(self.mode, pngquant_path, advpng_path)
        self.crunch.enable_tesseract(tesseract_path, self.force_ocr, self.no_ocr, self.tesseract_language)
        # lossless compressor
        self.cpdf = CPdfSqueezeCompressor(cpdfsqueeze_path, True)

    @staticmethod
    def get_config():
        config_path = os.path.abspath("../../config.json")
        if not os.path.isfile(config_path):
            raise FileNotFoundError("config.json not found, set the proper paths and run config.py")
        with open(config_path, "r") as config_file:
            json_config = jsons.loads(config_file.read())
            return json_config["pngquant_path"], json_config["advpng_path"], json_config["cpdfsqueeze_path"], json_config["tesseract_path"]


    def __parse_paths(self) -> None:
        # fills file_list with all pdf files that are going to be compressed
        # source_path is a folder -> len(file_list) >= 0 depending on how many files are found
        if os.path.isdir(self.source_path):
            if os.path.isfile(self.destination_path):
                raise ValueError(
                    "OptionError: If path is a directory the output_path must be one too!"
                )  # TODO make a merge possible

            elif self.uses_default_destination:
                self.destination_path = os.path.abspath(self.source_path) + "_compressed"

            self.source_file_list = OsUtility.get_file_list(self.source_path, ".pdf")

            for file in self.source_file_list:
                self.destination_file_list.append(
                    rf"{self.destination_path}/{OsUtility.get_filename(file)}.pdf")

        # source_path is a file -> len(file_list) == 1
        else:
            if self.uses_default_destination:
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
        # if len(self.source_file_list):
        #     self.__raise_value_error(f"Found no Pdf at -p/--path {self.source_path}")

    def compress_file_list(self) -> None:
        print(self.source_file_list, self.destination_file_list)
        for file, destination in zip(self.source_file_list, self.destination_file_list):
            # save size for comparison
            orig_size = os.stat(file).st_size

            print(file, destination)
            ConsoleUtility.print("compressing " + ConsoleUtility.get_file_string(file))

            # compress
            self.crunch.compress(file, destination)
            self.cpdf.compress(destination, destination)

            # if not force_ocr check if compression was successful
            size_after_compression = os.stat(destination).st_size
            if not self.force_ocr and orig_size < size_after_compression:
                # try compressing only with cpdf
                self.cpdf.compress(file, destination)
                cpdf_compression_only_size = os.stat(destination).st_size
                if orig_size < cpdf_compression_only_size:
                    ConsoleUtility.print(ConsoleUtility.get_error_string("File couldn't be compressed."))
                    shutil.copy(file, destination)
                else:
                    ConsoleUtility.print(ConsoleUtility.get_error_string(
                        "File couldn't be compressed using crunch cpdf combi. "
                        "However Cpdf could compress it. -> No OCR was Created. (force with -s/--force-ocr)"
                    ))

            ConsoleUtility.print_stats(orig_size, os.stat(destination).st_size)
            ConsoleUtility.print("created " + ConsoleUtility.get_file_string(destination))

    @staticmethod
    def __raise_value_error(error_string: str) -> None:
        ConsoleUtility.print(ConsoleUtility.get_error_string(error_string))
        raise ValueError(error_string)
