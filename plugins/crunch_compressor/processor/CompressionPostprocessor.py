import os.path
import re
from abc import ABC

from django_app.plugin_system.processing_classes.postprocessor import Postprocessor


class CompressionPostprocessor(Postprocessor, ABC):
    __compressor_name: str

    def __init__(self, compressor_name: str):
        self.__compressor_name = compressor_name

    def postprocess(self, source_file: str, destination_file: str) -> None:
        # page_number is the first number in the filename
        page_nuber = re.search(r'\d+\D', os.path.basename(source_file))[0]  # toto filename with number inside
        print(f"** - Compressed Page {page_nuber} with {self.__compressor_name}")
