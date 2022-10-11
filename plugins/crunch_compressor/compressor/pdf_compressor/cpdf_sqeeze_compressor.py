import os
import subprocess

from django_app import settings
from plugins.crunch_compressor.compressor.pdf_compressor.abstract_pdf_compressor import AbstractPdfCompressor
from plugins.crunch_compressor.utility.console_utility import ConsoleUtility
from plugins.crunch_compressor.utility.os_utility import OsUtility


class CPdfSqueezeCompressor(AbstractPdfCompressor):
    def __init__(
            self,
            cpdfsqueeze_path: str,
            wine_path_on_linux: str = "",
            user_password: str = None,
            owner_password: str = None,
            event_handlers=None
    ):
        """
        Pdf Compression via cpdf
        :param cpdfsqueeze_path: absolute path to executable
        :param wine_path_on_linux:
            True means it runs the command via wine.
                Only should be active when using linux or unix.
                If it is active on Windows, it will be automatically disabled.
            False means it directly runs the executable file at the path.
        """
        super().__init__(event_handlers, True)
        self.__cpdfsqueeze_path = cpdfsqueeze_path
        self.__wine_path_on_linux = wine_path_on_linux
        if os.name != "nt" and not os.path.exists(self.__wine_path_on_linux):
            raise ValueError(rf"wine_path couldn't be found. '{self.__wine_path_on_linux}'")
        if not os.path.exists(self.__cpdfsqueeze_path):
            raise ValueError(rf"cpdfsqueeze_path couldn't be found. '{self.__cpdfsqueeze_path}'")

        self.extra_args = ""
        if user_password is not None:
            self.extra_args += " -upw " + user_password
        if owner_password is not None:
            self.extra_args += " -opw " + owner_password

    def process_file(self, source_file: str, destination_file: str) -> None:
        self.preprocess(source_file, destination_file)
        if not os.path.exists(source_file) or not destination_file.endswith(".pdf"):
            raise ValueError("Only pdf files are accepted")

        command = self.__wine_path_on_linux + " " + self.__cpdfsqueeze_path
        # path arguments "from" "to"
        command += rf' "{source_file}" "{destination_file}"{self.extra_args}'
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except Exception as e:
            if settings.DEBUG:
                print(e)
            ConsoleUtility.print_error("[!] Compression Failed during CPdfSqueezeCompressor stage.")
            OsUtility.move_file(source_file, destination_file)
        self.postprocess(source_file, destination_file)
