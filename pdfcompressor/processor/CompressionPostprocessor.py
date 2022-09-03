from abc import ABC

from pdfcompressor.processor.postprocessor import Postprocessor
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility


class CompressionPostprocessor(Postprocessor, ABC):
    __compressor_name: str

    def __init__(self, compressor_name: str):
        self.__compressor_name = compressor_name

    def postprocess(self, source_file: str, destination_file: str) -> None:
        ConsoleUtility.print(
            f"** - Compressed Page {OsUtility.get_filename(source_file)[5:]} with {self.__compressor_name}"
        )
