import os
import subprocess
import sys
from subprocess import CalledProcessError

from .abstract_png_compressor import AbstractPngCompressor


class AdvanceCompressor(AbstractPngCompressor):
    def __init__(
            self,
            advpng_path: str,
            shrink_rate: int = 2,
            iterations: int = 1,
            event_handlers=None
    ):
        """
        Png Compressor via advpng
        :param shrink_rate (from 'https://www.advancemame.it/doc-advpng')
            -0, --shrink-store
                Disable the compression. The file is only stored and not compressed.
                The file is always rewritten also if it's bigger.
            -1, --shrink-fast
                Set the compression level to "fast" using the zlib compressor.
            -2, --shrink-normal
                Set the compression level to "normal" using the libdeflate compressor.
                This is the default level of compression.
            -3, --shrink-extra
                Set the compression level to "extra" using the 7z compressor.
                You can define the compressor iterations with the -i, --iter option.
            -4, --shrink-insane
                Set the compression level to "insane" using the zopfli compressor.
                You can define the compressor iterations with the -i, --iter option.

        :param iterations - amount of repetitions > 0
            more -> better compression but much slower
        """
        super().__init__(event_handlers, True)
        self.__advpng_path = advpng_path
        if not os.path.isfile(self.__advpng_path):
            raise FileNotFoundError(rf"advpng not found at '{self.__advpng_path}'")
        self.__system_extra = "powershell.exe" if os.name == 'nt' else ""

        if shrink_rate < 0 or shrink_rate > 4:
            raise ValueError("shrink_rate needs to be a value in range 0-4")
        if iterations < 0:
            raise ValueError("iterations need to be greater than 0")

        # compress, shrink-normal, 3 rounds of compression
        self.__advpng_options = " ".join(("--recompress", f"-{shrink_rate}", f"-i {iterations}"))

    def preprocess(self, source_file: str, destination_file: str) -> None:
        super().preprocess(source_file, destination_file)
        self._copy_file(source_file, destination_file)

    def postprocess(self, source_file: str, destination_file: str) -> None:
        if not self._is_valid_image(destination_file) or self._get_file_size(source_file) < self._get_file_size(
                destination_file):
            self._copy_file(source_file, destination_file)

        super().postprocess(source_file, destination_file)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        if not self._is_valid_image(source_file):
            raise ValueError(rf"'{source_file}' does not appear to be a valid path to a PNG file")

        advpng_command = rf"{self.__system_extra}  {self.__advpng_path} {self.__advpng_options} '{destination_path}'"
        try:
            subprocess.check_output(advpng_command, stderr=subprocess.STDOUT, shell=True)
        except CalledProcessError as cpe:
            print(repr(cpe), file=sys.stderr)
            print("processing failed at the advpng stage. (IGNORE)\n", file=sys.stderr)
            pass
        except Exception as e:
            print(repr(e), file=sys.stderr)  # dont raise e
        self.postprocess(source_file, destination_path)
