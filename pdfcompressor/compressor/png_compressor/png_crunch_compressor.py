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
        except FileNotFoundError:
            self.__advcomp = None
        try:
            self.__pngquant = PngQuantCompressor(
                pngquant_path,
                speed=pngquant_speed,
                min_quality=pngquant_min_quality,
                max_quality=pngquant_max_quality
            )
        except FileNotFoundError:
            self.__pngquant = None

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
