import os
import subprocess

from pdfcompressor.compressor.pdf_compressor.abstract_pdf_compressor import AbstractPdfCompressor
from pdfcompressor.utility.console_utility import ConsoleUtility


class CPdfSqueezeCompressor(AbstractPdfCompressor):
    def __init__(
            self,
            cpdfsqueeze_path: str,
            use_wine_on_linux: bool = False,
            user_password: str = None,
            owner_password: str = None
    ):
        """
        :param cpdfsqueeze_path: absolute path to executable
        :param use_wine_on_linux:
            True means it runs the command via wine.
                Only should be active when using linux or unix.
                If it is active on Windows, it will be automatically disabled.
            False means it directly runs the executable file at the path.
        """
        super().__init__()
        self.__cpdfsqueeze_path = cpdfsqueeze_path
        self.__use_wine = use_wine_on_linux and not "nt" == os.name
        if not os.path.exists(self.__cpdfsqueeze_path):
            raise ValueError(rf"cpdfsqueeze_path couldn't be found. '{self.__cpdfsqueeze_path}'")

        self.extra_args = ""
        if user_password is not None:
            self.extra_args += " -upw " + user_password
        if owner_password is not None:
            self.extra_args += " -opw " + owner_password

    def compress_file_list(self, source_files: list, destination_files: list) -> None:
        self.compress_file_list_multi_threaded(source_files, destination_files)

    def compress_file(self, source_file: str, destination_file: str) -> None:
        self.preprocess(source_file, destination_file)
        if not os.path.exists(source_file) or not destination_file.endswith(".pdf"):
            raise ValueError("Only pdf files are accepted")

        command = "wine " if self.__use_wine else ""
        command += self.__cpdfsqueeze_path
        # path arguments "from" "to"
        command += rf' "{source_file}" "{destination_file}"{self.extra_args}'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except Exception:
            ConsoleUtility.print_error("[!] Compression Failed during CPdfSqueezeCompressor stage.")
        self.postprocess(source_file, destination_file)
