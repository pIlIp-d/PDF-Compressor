import os

from .compressor_lib import crunch
from .cpdf_sqeeze_compressor import CPdfSqueezeCompressor
from ..utility.console_utility import ConsoleUtility
from ..utility.os_utility import OsUtility


class CrunchUtility:
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str
    ):
        if os.path.exists(pngquant_path):
            self._pngquant_path = pngquant_path
        else:
            ConsoleUtility.print(ConsoleUtility.get_error_string("Pngquant wasn't found at the given path (skipped)"))
            self._pngquant_path = None

        if os.path.exists(advpng_path):
            self._advpng_path = advpng_path
        else:
            ConsoleUtility.print(ConsoleUtility.get_error_string("Advpng wasn't found at the given path (skipped)"))
            self._advpng_path = None

    def crunch_list_of_files(self, image_list: list):
        ConsoleUtility.print("--Compressing via Crunch--")
        # parallel compression of single images
        args_list = [{
                "progress": image_id,
                "image": image_list[image_id],
                "length": len(image_list)
            } for image_id in range(len(image_list))]
        OsUtility.custom_map_execute(self.crunch, args_list)

        ConsoleUtility.print("** - 100.00%")

    def crunch(self, image: str, length: int, progress: int) -> None:
        crunched_file = image[:-4] + "-crunch.png"
        crunch.crunch(image, pngquant_path=self._pngquant_path, advpng_path=self._advpng_path, quiet_=True)
        try:
            os.remove(image)
        finally:
            os.rename(crunched_file, image)
        ConsoleUtility.print(f"** - Finished Page {progress + 1}/{length}")
