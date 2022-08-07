import os
import subprocess

from .abstract_pdf_compressor import AbstractPdfCompressor
from .compress_exception import CompressException
from .processor import Processor


class CPdfSqueezeCompressor(AbstractPdfCompressor):
    def __init__(self, cpdfsqueeze_path: str, use_wine_on_linux: bool = False, processor: Processor = None):
        """
        :param cpdfsqueeze_path: absolute path to executable
        :param use_wine_on_linux:
            True means it runs the command via wine.
                Only should be active when using linux or unix.
                If it is active on Windows, it will be automatically disabled.
            False means it directly runs the executable file at the path.
        """
        super().__init__(processor)
        self.__cpdfsqueeze_path = cpdfsqueeze_path
        self.__use_wine_on_linux = use_wine_on_linux and not "nt" == os.name
        if not os.path.exists(self.__cpdfsqueeze_path):
            raise ValueError(rf"cpdfsqueeze_path couldn't be found. '{self.__cpdfsqueeze_path}'")

    def compress_file(self, file: str, destination_file: str) -> None:
        if not os.path.exists(file) or not destination_file.endswith(".pdf"):
            raise ValueError("Only pdf files are accepted")

        command = "wine " if self.__use_wine_on_linux else ""
        command += self.__cpdfsqueeze_path
        # path arguments "from" "to"
        command += rf' "{file}" "{destination_file}"'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except Exception:  # TODO maybe disable custom exception
            raise CompressException("CPdfSqueezeCompressor")
