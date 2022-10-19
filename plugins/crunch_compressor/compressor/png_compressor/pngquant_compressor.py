import os
import subprocess
from subprocess import CalledProcessError

from plugins.crunch_compressor.compressor.png_compressor.abstract_png_compressor import AbstractPngCompressor
from django_app.utility.console_utility import ConsoleUtility


class PngQuantCompressor(AbstractPngCompressor):
    __FILE_SIZE_INCREASED_ERROR: int = 98
    __IMAGE_QUALITY_BELOW_LIMIT_ERROR: int = 99

    def __init__(
            self,
            pngquant_path: str,
            speed: int = 1,
            min_quality: int = 80,
            max_quality: int = 100,
            event_handlers=None
    ):
        """
        Png Compressor via pngquant
        :param speed 0:slowest and best quality, 10:fastest
        :param min_quality, max_quality 1-99
            Instructs pngquant to use the least amount of colors required to meet or exceed the max quality.
            If conversion results in quality below the min quality the image won't be saved
        :event_handlers - list of EventHandler
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

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)

        if not self._is_valid_image(source_file):
            raise ValueError(rf"'{source_file}' does not appear to be a valid path to a PNG file")

        pngquant_command = rf'{self.__system_extra}  {self.__pngquant_path} {self.__pngquant_options} "{source_file}"'
        try:
            subprocess.check_output(pngquant_command, stderr=subprocess.STDOUT, shell=True)
            result_file = source_file[:-4] + '-comp.png'
            self._compare_and_use_better_option(source_file, result_file, destination_path)
            if os.path.exists(result_file):
                os.remove(result_file)

        except CalledProcessError as cpe:
            if cpe.returncode in (self.__FILE_SIZE_INCREASED_ERROR, self.__IMAGE_QUALITY_BELOW_LIMIT_ERROR):
                pass
            else:
                ConsoleUtility.print_error("processing failed at the pngquant stage. (IGNORE)\n")
                pass
        except Exception as e:
            ConsoleUtility.print_error(repr(e))  # dont raise e
        self.postprocess(source_file, destination_path)
