from ...processor.processor import Processor
from .abstract_image_compressor import AbstractImageCompressor
from .advpng_compressor import AdvanceCompressor
from .pngquant_compressor import PngQuantCompressor


class PNGCrunchCompressor(AbstractImageCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
    ):
        super().__init__(".png", ".png")
        try:
            self.__advcomp = AdvanceCompressor(advpng_path)
        except FileNotFoundError:
            self.__advcomp = None
        try:
            self.__pngquant = PngQuantCompressor(pngquant_path)
        except FileNotFoundError:
            self.__pngquant = None

    @Processor.pre_and_post_processed
    def compress_file(self, source_file: str, destination_file: str) -> None:
        # run single file compress
        self.__pngquant.compress_file(source_file, destination_file)
        self.__advcomp.compress_file(destination_file, destination_file)

    def compress(self, source_path: str, destination_path: str) -> None:
        # run optimized compress
        self.__pngquant.compress(source_path, destination_path)
        self.__advcomp.compress(destination_path, destination_path)
