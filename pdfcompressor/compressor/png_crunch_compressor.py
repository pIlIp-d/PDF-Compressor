import os
import shutil

from .compressor import Compressor
from .crunch_utility import CrunchUtility
from ..io_path_parser import IOPathParser
from pdfcompressor.compressor.processor import Processor


class PNGCrunchCompressor(Compressor):
    def __init__(
            self,
            pngquant_path: str,
            advpng_path: str,
            processor: Processor = None
    ):
        self.__crunch_utility = CrunchUtility(pngquant_path, advpng_path)
        self._processors = [processor] if processor is not None else []

    @staticmethod
    def __get_temp_folder() -> str:
        number = 0
        while os.path.exists("./temp_" + str(number)):
            number += 1
        return os.path.abspath("./temp_" + str(number)) + os.path.sep

    def postprocess(self, source: str, destination: str) -> None:
        # move files to destination
        shutil.copy(source, destination)
        super().postprocess(source, destination)

    def compress(self, source_path: str, destination_path: str) -> None:  # TODO console messages
        source_path = rf"{os.path.abspath(source_path)}"
        destination_path = rf"{os.path.abspath(destination_path)}"

        io_path_parser = IOPathParser(source_path, destination_path, ".png", ".png", "_compressed")
        source_file_list = io_path_parser.get_input_file_paths()
        destination_file_list = io_path_parser.get_output_file_paths()

        if io_path_parser.is_merging():
            raise ValueError("when a folder is the input a file can't be the output. (cant merge)")

        temp_folder = self.__get_temp_folder()

        # gets filled with image paths in preprocessing
        temp_images_list = []

        for file, destination in zip(source_file_list, destination_file_list):
            self.preprocess(file, destination)
            # moving all the files into temp folder
            new_path = os.path.join(temp_folder + os.path.basename(file))
            shutil.copy(file, new_path)
            temp_images_list.append(new_path)

        self.__crunch_utility.crunch_list_of_files(temp_images_list)

        for file, destination in zip(temp_images_list, destination_file_list):
            self.postprocess(file, destination)

        shutil.rmtree(temp_folder, ignore_errors=True)
