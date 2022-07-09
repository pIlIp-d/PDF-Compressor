from Compressor import *
import compressor_lib.crunch as crunch
import os


class CrunchCompressor(Compressor):

    def __init__(self, origin_path, dest_path, pngquant_path, advpng_path):
        super().__init__(origin_path, dest_path)
        self.pngquant_path = pngquant_path
        self.advpng_path = advpng_path

    def compress(self):
        crunched_file = self.origin_path[:-4] + "-crunch.png"
        crunch.crunch(self.origin_path, pngquant_path=self.pngquant_path, advpng_path=self.advpng_path, quiet_=True)
        try:
            os.remove(self.dest_path)
        finally:
            os.rename(crunched_file, self.dest_path)
