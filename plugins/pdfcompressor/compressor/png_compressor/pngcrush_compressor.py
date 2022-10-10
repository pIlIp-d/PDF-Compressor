import os
import subprocess
from subprocess import CalledProcessError

from plugins.pdfcompressor.compressor.png_compressor.abstract_image_compressor import AbstractImageCompressor
from plugins.pdfcompressor.utility.EventHandler import EventHandler
from plugins.pdfcompressor.utility.console_utility import ConsoleUtility
from plugins.pdfcompressor.utility.os_utility import OsUtility


class PngcrushCompressor(AbstractImageCompressor):

    def __init__(
            self,
            pngcrush_path: str,
            event_handlers: list[EventHandler] = list()
    ):
        super().__init__(".png", ".png", event_handlers)
        self.__pngcrush_path = pngcrush_path

        if not os.path.isfile(self.__pngcrush_path):
            raise FileNotFoundError(rf"pngcrush not found at '{self.__pngcrush_path}'")

        self.__system_extra = "powershell.exe" if os.name == 'nt' else ""
        self.__pngquant_options = "-rem alla -rem text -reduce" # -brute"

    def postprocess(self, source_file: str, destination_file: str) -> None:
        crunch_destination = source_file[:-4] + '-comp.png'
        original_size = OsUtility.get_file_size(source_file)
        result_size = OsUtility.get_file_size(crunch_destination)

        # compression worked -> copy file to final destination
        if self._is_valid_image(crunch_destination) and original_size > result_size:
            OsUtility.copy_file(crunch_destination, destination_file)
        # error in output file -> copy source file to destination
        else:
            OsUtility.copy_file(source_file, destination_file)

        if os.path.exists(crunch_destination):
            os.remove(crunch_destination)

        super().postprocess(source_file, destination_file)

    def compress_file(self, source_file: str, destination_file: str) -> None:
        self.preprocess(source_file, destination_file)

        if not self._is_valid_image(source_file):
            raise ValueError(rf"'{source_file}' does not appear to be a valid path to a PNG file")

        pngcrush_command = rf'{self.__system_extra} {self.__pngcrush_path} ' \
                           rf'{self.__pngquant_options} "{source_file}" "{source_file[:-4] + "-comp.png"}"'

        try:
            subprocess.check_output(pngcrush_command, stderr=subprocess.STDOUT, shell=True)
        except CalledProcessError as cpe:
            ConsoleUtility.print_error(str(cpe))
            ConsoleUtility.print_error("processing failed at the pngcrush stage. (IGNORE)\n")
            pass
        except Exception as e:
            ConsoleUtility.print_error(repr(e))  # dont raise e
        self.postprocess(source_file, destination_file)
