import re
from abc import ABC

from plugins.pdfcompressor.processor.postprocessor import Postprocessor
from plugins.pdfcompressor.utility.console_utility import ConsoleUtility
from plugins.pdfcompressor.utility.os_utility import OsUtility


class CompressionPostprocessor(Postprocessor, ABC):
    __compressor_name: str

    def __init__(self, compressor_name: str):
        self.__compressor_name = compressor_name

    def postprocess(self, source_file: str, destination_file: str) -> None:
        # page_number is the first number in the filename
        page_nuber = re.search(r'\d+', OsUtility.get_filename(source_file))[0]
        ConsoleUtility.print(
            f"** - Compressed Page {page_nuber} with {self.__compressor_name}"
        )