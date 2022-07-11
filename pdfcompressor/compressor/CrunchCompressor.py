import multiprocessing
import os

from pdfcompressor.compressor.Compressor import Compressor
from pdfcompressor.compressor.converter.ImagesToPdfConverter import ImagesToPdfConverter
from pdfcompressor.compressor.converter.PdfToImageConverter import PdfToImageConverter
from pdfcompressor.utility.ConsoleUtility import ConsoleUtility
from pdfcompressor.utility.OsUtility import OsUtility
import pdfcompressor.compressor.compressor_lib.crunch as crunch


class CrunchCompressor(Compressor):

    def __init__(
            self,
            mode: int,
            pngquant_path: str,
            advpng_path: str
    ):
        # set default values
        self.source_path = None
        self.destination_path = None
        self.temp_folder = None
        self.tesseract_path = None
        self.force_ocr = False
        self.no_ocr = None
        self.tesseract_language = None

        if mode <= 0 or mode >= 11:
            raise Exception("TODO")  # TODO
        if not os.path.exists(pngquant_path):
            raise Exception("TODO")  # TODO
        if not os.path.exists(advpng_path):
            raise Exception("TODO")  # TODO

        self.mode = mode
        self.pngquant_path = pngquant_path
        self.advpng_path = advpng_path

    def enable_tesseract(
            self,
            tesseract_path: str,
            force_ocr: bool = False,
            no_ocr: bool = False,
            tesseract_language: str = "deu"
    ) -> None:

        if not os.path.exists(tesseract_path):
            raise Exception("TODO")  # TODO
        self.tesseract_path = tesseract_path
        self.force_ocr = force_ocr
        self.no_ocr = no_ocr
        self.tesseract_language = tesseract_language

    def __preprocess(self) -> None:
        # create folder for temporary files(images...)
        OsUtility.create_folder_if_not_exist(self.temp_folder)
        # split pdf into images that can be compressed using crunch
        PdfToImageConverter(self.source_path, self.temp_folder, self.mode).convert()

    def __postprocess(self) -> None:
        OsUtility.create_folder_if_not_exist(self.destination_path)
        # merge images/pages into new pdf and optionally apply OCR
        ImagesToPdfConverter(self.temp_folder, self.destination_path, self.tesseract_path, self.force_ocr, self.tesseract_language).convert()
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
                self.__crunch,  # method
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

    def __crunch(self, image_list: str, length: int, progress: int) -> None:
        crunched_file = image_list[:-4] + "-crunch.png"
        crunch.crunch(image_list, pngquant_path=self.pngquant_path, advpng_path=self.advpng_path, quiet_=True)
        try:
            os.remove(image_list)
        finally:
            os.rename(crunched_file, image_list)
        ConsoleUtility.print("** - {:.2f}%".format(100 * progress / length))