import os
import subprocess
from subprocess import CalledProcessError

from pdfcompressor.compressor.png_compressor.abstract_image_compressor import AbstractImageCompressor
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility

# todo play with the options of the compression tools to achieve the best results


class PngQuantCompressor(AbstractImageCompressor):
    __FILE_SIZE_INCREASED_ERROR: int = 98
    __IMAGE_QUALITY_BELOW_LIMIT_ERROR: int = 99

    def __init__(self, pngquant_path: str):
        super().__init__(".png", ".png")
        self.__pngquant_path = pngquant_path

        if not os.path.isfile(self.__pngquant_path):
            raise FileNotFoundError(rf"pngquant not found at '{self.__pngquant_path}'")
        self.__system_extra = "powershell.exe" if os.name == 'nt' else ""
        self.__pngquant_options = " ".join((
            "--quality=80-98",
            "--skip-if-larger",
            "--force",
            "--speed 1",
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
