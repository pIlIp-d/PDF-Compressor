import os
import subprocess
from subprocess import CalledProcessError

from plugins.crunch_compressor.compressor.png_compressor.abstract_png_compressor import AbstractPngCompressor
from plugins.crunch_compressor.utility.EventHandler import EventHandler
from plugins.crunch_compressor.utility.console_utility import ConsoleUtility
from plugins.crunch_compressor.utility.os_utility import OsUtility


class PngQuantCompressor(AbstractPngCompressor):
    __FILE_SIZE_INCREASED_ERROR: int = 98
    __IMAGE_QUALITY_BELOW_LIMIT_ERROR: int = 99

    def __init__(
            self,
            pngquant_path: str,
            speed: int = 1,
            min_quality: int = 80,
            max_quality: int = 100,
            event_handlers: list[EventHandler] = list()
    ):
        """
        :param speed 0:slowest and best quality, 10:fastest
        :param min_quality, max_quality 1-99
            Instructs pngquant to use the least amount of colors required to meet or exceed the max quality.
            If conversion results in quality below the min quality the image won't be saved
        """
        super().__init__(event_handlers)
        self.__pngquant_path = pngquant_path

        if not os.path.isfile(self.__pngquant_path):
            raise FileNotFoundError(rf"pngquant not found at '{self.__pngquant_path}'")

        if speed < 0 or speed > 10:
            raise ValueError("speed needs to be a value in range 0-10")
        if min_quality < 0 or min_quality >= 100:
            raise ValueError("min_quality needs to be between 0 and 100")
        if max_quality < 0 or max_quality < min_quality:
            raise ValueError("max_quality need to be greater than 0 and min_quality")

        self.__system_extra = "powershell.exe" if os.name == 'nt' else ""
        self.__pngquant_options = " ".join((
            f"--quality={min_quality}-{max_quality}",
            "--skip-if-larger",
            "--force",
            f"--speed {speed}",
            "--strip",
            "--ext '-comp.png'"
        ))

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

        pngquant_command = rf'{self.__system_extra}  {self.__pngquant_path} {self.__pngquant_options} "{source_file}"'
        try:
            subprocess.check_output(pngquant_command, stderr=subprocess.STDOUT, shell=True)
        except CalledProcessError as cpe:
            if cpe.returncode in (self.__FILE_SIZE_INCREASED_ERROR, self.__IMAGE_QUALITY_BELOW_LIMIT_ERROR):
                pass
            else:
                ConsoleUtility.print_error("processing failed at the pngquant stage. (IGNORE)\n")
                pass
        except Exception as e:
            ConsoleUtility.print_error(repr(e))  # dont raise e
        self.postprocess(source_file, destination_file)
