import multiprocessing
import os
import shutil

from .compressor import Compressor
from .compressor_lib import crunch
from .converter.images_to_pdf_converter import ImagesToPdfConverter
from .converter.pdf_to_image_converter import PdfToImageConverter
from ..utility.console_utility import ConsoleUtility
from ..utility.os_utility import OsUtility


class CrunchCompressor(Compressor):

    def __init__(
            self,
            mode: int,
            pngquant_path: str,
            advpng_path: str
    ):
        # set default values
        self.tessdata_prefix = None
        self.source_path = None
        self.destination_path = None
        self.temp_folder = None
        self.tesseract_path = None
        self.force_ocr = False
        self.no_ocr = None
        self.tesseract_language = None

        if mode <= 0 or mode >= 11:
            raise ValueError("TODO")  # TODO
        if not os.path.exists(pngquant_path):
            raise ValueError("TODO")  # TODO
        if not os.path.exists(advpng_path):
            raise ValueError("TODO")  # TODO

        self.mode = mode

        if os.path.exists(pngquant_path):
            self.pngquant_path = pngquant_path
        else:
            self.pngquant_path = None

        if os.path.exists(advpng_path):
            self.advpng_path = advpng_path
        else:
            self.advpng_path = None

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
                raise ValueError("If force-ocr is active tesseract needs to be configured correctly.")
            else:
                tesseract_path = None
        self.tesseract_path = tesseract_path
        self.force_ocr = force_ocr
        self.no_ocr = no_ocr
        self.tesseract_language = tesseract_language
        self.tessdata_prefix = tessdata_prefix

    def __preprocess(self) -> None:
        # create new empty folder for temporary files
        shutil.rmtree(self.temp_folder, ignore_errors=True)
        os.makedirs(self.temp_folder)
        # split pdf into images that can be compressed using crunch
        PdfToImageConverter(self.source_path, self.temp_folder, self.mode).convert()

    def __postprocess(self) -> None:
        if self.destination_path.endswith(".pdf"):
            os.makedirs(os.path.dirname(self.destination_path), exist_ok=True)
        else:
            os.makedirs(self.destination_path, exist_ok=True)
        # merge images/pages into new pdf and optionally apply OCR
        ImagesToPdfConverter(
            self.temp_folder,
            self.destination_path,
            self.tesseract_path,
            self.force_ocr,
            self.no_ocr,
            self.tesseract_language,
            self.tessdata_prefix
        ).convert()
        OsUtility.clean_up_folder(self.temp_folder)

    def compress(
            self,
            source_path: str,
            destination_path: str
    ) -> None:

        self.source_path = source_path
        self.destination_path = destination_path
        self.temp_folder = os.path.abspath(
            (OsUtility.get_filename(source_path) + "_tmp").replace(" ", "_")) + os.path.sep

        self.__preprocess()

        # list of pdf pages in png format
        image_list = OsUtility.get_file_list(self.temp_folder, ".png")

        ConsoleUtility.print("--Compressing via Crunch--")
        pool = multiprocessing.Pool()
        try:
            # multithreaded compression of single images
            # parameter is function and splitted imgs list with some length counts to display progress
            pool.starmap(
                self.crunch,  # method
                zip(image_list,  # parameters - as list of pairs of 3 (zipped)
                    [len(image_list) for y in range(len(image_list))],
                    [z for z in range(len(image_list))]
                    )
            )

        except KeyboardInterrupt:
            # shutil.rmtree(folder)#clean up
            pool.terminate()
            pool.join()
            quit()
        except Exception as e:
            # shutil.rmtree(folder)#clean up after failure
            raise e
        finally:  # To make sure processes are closed in the end, even if errors happen
            pool.close()
            pool.join()
            ConsoleUtility.print("** - 100.00%")  # final progress step

        self.__postprocess()

    def crunch(self, image_list: str, length: int, progress: int) -> None:
        crunched_file = image_list[:-4] + "-crunch.png"
        crunch.crunch(image_list, pngquant_path=self.pngquant_path, advpng_path=self.advpng_path, quiet_=True)
        try:
            os.remove(image_list)
        finally:
            os.rename(crunched_file, image_list)
        ConsoleUtility.print("** - {:.2f}%".format(100 * progress / length))
