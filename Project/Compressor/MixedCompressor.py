from Project.Compressor.Compressor import Compressor
from Project.Compressor.CPdfSqeezeCompressor import CPdfSqueezeCompressor
from Project.Compressor.CrunchCompressor import CrunchCompressor


class MixedCompressor(Compressor):
    def __init__(self, origin_path, dest_path, cpdfsqueeze_path, pngquant_path, advpng_path):
        super().__init__(origin_path, dest_path)
        self.cpdf = CPdfSqueezeCompressor(origin_path, dest_path, cpdfsqueeze_path)
        self.crunch = CrunchCompressor(origin_path, dest_path, pngquant_path, advpng_path)

    def compress(self):
        self.cpdf.compress()
        self.crunch.compress()
