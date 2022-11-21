from .abstract_png_compressor import AbstractPngCompressor
from .advpng_compressor import AdvanceCompressor
from .pngcrush_compressor import PngcrushCompressor
from .pngquant_compressor import PngQuantCompressor
from ...processor.CompressionPostprocessor import CompressionPostprocessor
from django_app.utility.console_utility import ConsoleUtility


class PNGCrunchCompressor(AbstractPngCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            pngcrush_path: str,
            compression_mode: int = 3,
            event_handlers=None
    ):
        super().__init__(event_handlers, False)

        if compression_mode <= 0 or compression_mode >= 6:
            raise ValueError("Compression mode must be in range 1-5")

        # chosen values after some testing using grid search measurement and plotting (https://www.csvplot.com/)
        advcomp_iterations = 3 if compression_mode == 1 else 2 if compression_mode == 2 else 1
        advcomp_shrink_rate = \
            4 if compression_mode == 1 else 3 if compression_mode == 2 else 2 if 3 <= compression_mode <= 4 else 1
        pngquant_max_quality = \
            80 if compression_mode == 1 else 85 if 2 <= compression_mode <= 3 else 90 if compression_mode == 4 else 99
        pngquant_min_quality = 0 if compression_mode == 1 else 25
        pngquant_speed = \
            1 if compression_mode == 1 else 2 if 2 <= compression_mode <= 3 else 8 if compression_mode == 4 else 9

        try:
            self.__advcomp = AdvanceCompressor(
                advpng_path,
                shrink_rate=advcomp_shrink_rate,
                iterations=advcomp_iterations
            )
            self.__advcomp.add_postprocessor(CompressionPostprocessor("advcomp"))
        except FileNotFoundError:
            ConsoleUtility.print_error("Error: Program advcomp not found, skipped compression with advcomp.")
            self.__advcomp = None

        try:
            self.__pngquant = PngQuantCompressor(
                pngquant_path,
                speed=pngquant_speed,
                min_quality=pngquant_min_quality,
                max_quality=pngquant_max_quality
            )
            self.__pngquant.add_postprocessor(CompressionPostprocessor("pngquant"))
        except FileNotFoundError:
            ConsoleUtility.print_error("Error: Program pngquant not found, skipped compression with pngquant.")
            self.__pngquant = None

        try:
            self.__pngcrush = PngcrushCompressor(
                pngcrush_path
            )
            self.__pngcrush.add_postprocessor(CompressionPostprocessor("pngcrush"))
        except FileNotFoundError:
            ConsoleUtility.print_error("Error: Program pngcrush not found, skipped compression with pngcrush.")
            self.__pngcrush = None

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)

        # run single file compress
        if self.__pngquant is not None:
            self.__pngquant.process_file(source_file, destination_path)
        if self.__advcomp is not None:
            self.__advcomp.process_file(destination_path, destination_path)
        if self.__pngcrush is not None:
            self.__pngcrush.process_file(source_file, destination_path)
        self.postprocess(source_file, destination_path)

    def _process_file_list(self, source_files: list, destination_files: list) -> None:
        # run optimized compress
        if self.__pngquant is not None:
            self.__pngquant.process_file_list_multi_threaded(source_files, destination_files)
        if self.__advcomp is not None:
            self.__advcomp.process_file_list_multi_threaded(source_files, destination_files)
        if self.__pngcrush is not None:
            self.__pngcrush.process_file_list_multi_threaded(source_files, destination_files)
