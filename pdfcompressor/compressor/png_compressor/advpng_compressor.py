import os
import subprocess
from subprocess import CalledProcessError

from .abstract_image_compressor import AbstractImageCompressor
from ...processor.postprocessor import Postprocessor
from ...processor.processor import Processor
from ...utility.console_utility import ConsoleUtility
from ...utility.os_utility import OsUtility


# todo play with the options of the compression tools to achieve the best results


class AdvanceCompressor(AbstractImageCompressor):
    def __init__(self, advpng_path: str):
        super().__init__(".png", ".png")
        self.__advpng_path = advpng_path
        if not os.path.isfile(self.__advpng_path):
            raise FileNotFoundError(rf"advpng not found at '{self.__advpng_path}'")
        self.__system_extra = "powershell.exe" if os.name == 'nt' else ""
        # compress, shrink-normal, 3 rounds of compression
        self.__advpng_options = ("--recompress", "--shrink-normal", "-i 3")  # todo mode changeable

    def postprocess(self, source_file: str, destination_file: str) -> None:
        if not self._is_valid_image(destination_file) or OsUtility.get_file_size(source_file) < OsUtility.get_file_size(
                destination_file):
            OsUtility.copy_file(source_file, destination_file)
        super().postprocess(source_file, destination_file)

    @Processor.pre_and_post_processed
    def compress_file(self, source_file: str, destination_file: str) -> None:
        if not self._is_valid_image(source_file):
            raise ValueError(rf"'{source_file}' does not appear to be a valid path to a PNG file")

        advpng_command = (rf"{self.__system_extra}  {self.__advpng_path} {' '.join(self.__advpng_options)} '{source}'")
        try:
            subprocess.check_output(advpng_command, stderr=subprocess.STDOUT, shell=True)
        except CalledProcessError as cpe:
            print(cpe)
            ConsoleUtility.print(ConsoleUtility.get_error_string("processing failed at the advpng stage. (IGNORE)\n"))
            pass
        except Exception as e:
            ConsoleUtility.print_error(repr(e))  # dont raise e
