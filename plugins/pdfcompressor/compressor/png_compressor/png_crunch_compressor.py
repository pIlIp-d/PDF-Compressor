from .abstract_image_compressor import AbstractImageCompressor
from .advpng_compressor import AdvanceCompressor
from .pngcrush_compressor import PngcrushCompressor
from .pngquant_compressor import PngQuantCompressor
from ...processor.CompressionPostprocessor import CompressionPostprocessor
from ...utility.EventHandler import EventHandler
from ...utility.console_utility import ConsoleUtility


class PNGCrunchCompressor(AbstractImageCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            pngcrush_path: str,
            compression_mode: int = 3,
            event_handlers: list[EventHandler] = list()
    ):
        super().__init__(".png", ".png", event_handlers)

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

    def compress_file(self, source_file: str, destination_file: str) -> None:
        self.preprocess(source_file, destination_file)

        # run single file compress
        if self.__pngquant is not None:
            self.__pngquant.compress_file(source_file, destination_file)
        if self.__advcomp is not None:
            self.__advcomp.compress_file(destination_file, destination_file)
        if self.__pngcrush is not None:
            self.__pngcrush.compress_file(source_file, destination_file)
        self.postprocess(source_file, destination_file)

    def compress_file_list(self, source_files: list, destination_files: list) -> None:
        # run optimized compress
        if self.__pngquant is not None:
            self.__pngquant.compress_file_list(source_files, destination_files)
        if self.__advcomp is not None:
            self.__advcomp.compress_file_list(source_files, destination_files)
        if self.__pngcrush is not None:
            self.__pngcrush.compress_file_list(source_files, destination_files)