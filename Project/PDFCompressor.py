#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================
import os

import argparse
import shutil

from Project.Compressor.CPdfSqeezeCompressor import CPdfSqueezeCompressor
from Project.Compressor.Compressor import Compressor
from Project.Compressor.CrunchCompressor import CrunchCompressor
from Project.Utility.ConsoleUtility import ConsoleUtility
from Project.Utility.OsUtility import OsUtility

if os.name == "nt":
    PNGQUANT_PATH = os.path.join(os.path.dirname(__file__), "Compressor/compressor_lib", "pngquant", "pngquant.exe")
    ADVPNG_PATH = os.path.join(os.path.dirname(__file__), "Compressor/compressor_lib", "advpng", "advpng.exe")
else:
    PNGQUANT_PATH = os.path.join("/", "usr", "bin", "pngquant")
    ADVPNG_PATH = os.path.join("/", "usr", "bin", "advpng")
    TESSERACT_PATH = os.path.join("/", "home", "user", ".local", "bin", "pytesseract")
    if not os.path.exists(PNGQUANT_PATH):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string("Pngquant path not found. Install it with 'sudo apt install pngquant'."))
        exit()
    if not os.path.exists(ADVPNG_PATH):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string("advpng path not found. Install it with 'sudo apt install advancecomp'."))
        exit()
    if not os.path.exists(TESSERACT_PATH):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string("pytesseract path not found. Install it with 'sudo apt install "
                                            "pytesseract-ocr'. Additionally add language packs with f.e. "
                                            "'german/deutsch': 'sudo apt install pytesseract-ocr-deu'"))
        exit()

CPDFSQUEEZE_PATH = os.path.join(os.path.dirname(__file__), "Compressor/compressor_lib", "cpdfsqueeze",
                                "cpdfsqueeze.exe")


class PDFCompressor:

    def __init__(
            self,
            source_path: str,
            destination_path: str,
            mode: int,
            continue_position: int = 0,
            force_ocr: bool = False,
            no_ocr: bool = False
    ):
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
                "option -c --continue must be greater than or equals to 0"
            )

        self.source_path = rf"{os.path.abspath(source_path)}"
        self.destination_path = rf"{os.path.abspath(destination_path)}"
        self.__parse_paths()

        self.mode = mode
        self.continue_position = continue_position
        self.force_ocr = force_ocr
        self.no_ocr = no_ocr
        self.source_file_list = []
        self.destination_file_list = []

        # save size for comparison
        self.orig_size = os.stat(self.source_path).st_size

        self.compress_file_list()

    def __parse_paths(self):
        # fills file_list with all pdf files that are going to be compressed
        # source_path is a folder -> len(file_list) >= 0 depending on how many files are found
        if os.path.isdir(self.source_path):
            if os.path.isfile(self.destination_path):
                raise ValueError(
                    "OptionError: If path is a directory the output_path must be one too!")  # TODO make a merge possible

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

    def compress_file_list(self):
        # lossy compressor
        crunch = CrunchCompressor(self.mode, PNGQUANT_PATH, ADVPNG_PATH)
        # lossless compressor
        cpdf = CPdfSqueezeCompressor(CPDFSQUEEZE_PATH, True)

        for file, destination in self.source_file_list, self.destination_file_list:
            ConsoleUtility.print("compressing " + ConsoleUtility.get_file_string(pdf_file))

            # compress
            crunch.compress(file, destination)
            cpdf.compress(destination, destination)

            # if not force_ocr check if compression was successful
            size_after_compression = os.stat(destination).st_size
            if not self.force_ocr and self.orig_size < size_after_compression:
                # try compressing only with cpdf
                cpdf.compress(file, destination)
                cpdf_compression_only_size = os.stat(destination).st_size
                if self.orig_size < cpdf_compression_only_size:
                    shutil.copy(pdf_file, output_file)
                else:
                    ConsoleUtility.print(ConsoleUtility.get_error_string("File couldn't be compressed."))
                ConsoleUtility.print(ConsoleUtility.get_error_string("No OCR created."))

            ConsoleUtility.print_stats(self.orig_size, os.stat(destination).st_size)
            ConsoleUtility.print("created " + ConsoleUtility.get_file_string(destination))

    @staticmethod
    def __raise_value_error(error_string: str):
        ConsoleUtility.print(ConsoleUtility.get_error_string(error_string))
        raise ValueError(error_string)  # TODO

    def old__init__(self, crunch: Compressor, origin_pdf, output_pdf, mode=5, force_ocr=True, continue_arg=0):
        if continue_arg < 0:
            ConsoleUtility.print("option -c --continue must be greater than or equals to 0")
            raise Exception("option continue must be greater than or equal to 0")  # TODO

        # print filename in yellow
        ConsoleUtility.print("--Compressing " + ConsoleUtility.get_file_string(pdf_file) + "--")

        # save size for comparison
        orig_size = os.stat(pdf_file).st_size

        # compress lossy
        crunch = CrunchCompressor(mode, PNGQUANT_PATH, ADVPNG_PATH)
        crunch.enable_tesseract(TESSERACT_PATH, force_ocr)
        crunch.compress(origin_pdf, output_file)

        # compress pdf lossless
        CPdfSqueezeCompressor(output_file, output_file, CPDFSQUEEZE_PATH, True).compress()

        # discard progress if not smaller. try simple compression with cpdfsqueeze instead
        if orig_size < os.stat(output_file).st_size and not force_ocr:
            CPdfSqueezeCompressor(pdf_file, output_file, CPDFSQUEEZE_PATH, True).compress()
            if orig_size < os.stat(output_file).st_size:
                shutil.copy(pdf_file, output_file)
            ConsoleUtility.print(ConsoleUtility.get_error_string("No OCR created."))

        ConsoleUtility.print_stats(orig_size, os.stat(output_file).st_size)
        ConsoleUtility.print("created " + ConsoleUtility.get_file_string(output_file))


def get_args():
    all_args = argparse.ArgumentParser(prog='PDF Compress', usage='%(prog)s [options]',
                                       description='Compresses PDFs using lossy png and lossless PDF compression. '
                                                   'Optimized for GoodNotes')
    all_args.add_argument("-p", "--path", required=True, help="Path to pdf file or to folder containing pdf files")
    all_args.add_argument("-m", "--mode", required=False, type=int,
                          help="compression mode 1-10. 1:high 10:low compression. Default=3", default=3)
    all_args.add_argument("-o", "--output-path", required=False,
                          help="Compressed file Output Path. Default: 'filename_compressed.pdf' or 'compressed/...' for "
                               "folders",
                          default="default")
    all_args.add_argument("-s", "--force-ocr", required=False, action='store_true',
                          help="When turned on allows output file to be larger than input file, to force ocr. "
                               "Default: off and only smaller output files are saved.'")
    all_args.add_argument("-n", "--no-ocr", required=False, action='store_true', help="Don't create OCR on pdf.")
    all_args.add_argument("-c", "--continue", required=False, type=int,
                          help="Number. When compressing folder and Interrupted, skip files already converted. ("
                               "=amount of files already converted)",
                          default=0)
    args = vars(all_args.parse_args())
    return args, all_args


if __name__ == "__main__":
    args, args_obj = get_args()
    path, output_path, is_dir = get_paths_from_args(args)

    if len(path) == 0:
        ConsoleUtility.print(ConsoleUtility.get_error_string("No PDF Found!"))
        quit(-1)
    # compress either single file or all files in folder

    for pdf_file in path[args["continue"]:]:  # start with element at position --continue parameter
        # remove .pdf, path (only Filename)
        pdf_name = OsUtility.get_filename(pdf_file)

        output_file = os.path.abspath(output_path)
        if is_dir:
            output_file = os.path.join(output_path, pdf_name) + ".pdf"
        PDFCompressor(pdf_file, output_file, args['mode'], args['force_ocr'])
