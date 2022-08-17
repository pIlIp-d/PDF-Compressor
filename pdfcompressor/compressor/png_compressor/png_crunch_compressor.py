from ...processor.processor import Processor
from .abstract_image_compressor import AbstractImageCompressor
from .advpng_compressor import AdvanceCompressor
from .pngquant_compressor import PngQuantCompressor


class PNGCrunchCompressor(AbstractImageCompressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            compression_mode: int = 3
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

        if compression_mode <= 0 or compression_mode >= 11:
            raise ValueError("Compression mode must be between 1 and 10")
        self.__compressing_mode = compression_mode

    def compress_file(self, source_file: str, destination_file: str) -> None:
        self.preprocess(source_file, destination_file)

        # run single file compress
        self.__pngquant.compress_file(source_file, destination_file)
        self.__advcomp.compress_file(destination_file, destination_file)
        self.postprocess(source_file, destination_file)

    def compress(self, source_path: str, destination_path: str) -> None:
        # run optimized compress
        self.__pngquant.compress(source_path, destination_path)
        self.__advcomp.compress(destination_path, destination_path)
