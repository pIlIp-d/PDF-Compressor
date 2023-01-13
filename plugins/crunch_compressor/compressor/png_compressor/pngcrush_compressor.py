import os
import subprocess
import sys
from subprocess import CalledProcessError

from plugins.crunch_compressor.compressor.png_compressor.abstract_png_compressor import AbstractPngCompressor


class PngcrushCompressor(AbstractPngCompressor):

    def __init__(
            self,
            pngcrush_path: str,
            event_handlers=None
    ):
        super().__init__(event_handlers, True)
        self.__pngcrush_path = pngcrush_path

        if not os.path.isfile(self.__pngcrush_path):
            raise FileNotFoundError(rf"pngcrush not found at '{self.__pngcrush_path}'")

        self.__system_extra = "powershell.exe" if os.name == 'nt' else ""
        self.__pngquant_options = "-rem alla -rem text -reduce"  # -brute"
        # TODO add option brute when compression mode is high

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)

        if not self._is_valid_image(source_file):
            raise ValueError(rf"'{source_file}' does not appear to be a valid path to a PNG file")

        pngcrush_command = rf'{self.__system_extra} {self.__pngcrush_path} ' \
                           rf'{self.__pngquant_options} "{source_file}" "{source_file[:-4] + "-comp.png"}"'

        try:
            subprocess.check_output(pngcrush_command, stderr=subprocess.STDOUT, shell=True)
            result_file = source_file[:-4] + '-comp.png'
            self._compare_and_use_better_option(source_file, result_file, destination_path)
            if os.path.exists(result_file):
                os.remove(result_file)
        except CalledProcessError as cpe:
            print(repr(cpe), file=sys.stderr)
            print("processing failed at the pngcrush stage. (IGNORE)\n", file=sys.stderr)
        except Exception as e:
            print(repr(e), file=sys.stderr)  # dont raise e
        self.postprocess(source_file, destination_path)
