import os
import subprocess

from .compress_exception import CompressException
from .compressor import Compressor


class CPdfSqueezeCompressor(Compressor):
    def __init__(
            self,
            cpdfsqueeze_path: str,
            use_wine_on_linux: bool = False
    ):
        self.cpdfsqueeze_path = cpdfsqueeze_path
        self.use_wine_on_linux = use_wine_on_linux

    def compress(
            self,
            source_path: str,
            destination_path: str
    ) -> None:
        command = ""
        if self.use_wine_on_linux and not "nt" == os.name:
            command += "wine "
        command += self.cpdfsqueeze_path
        # compress file from origin_path to dest_path
        command += ' "' + source_path + '" "' + destination_path + '"'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except Exception:
            raise CompressException("CPdfSqueezeCompressor")
