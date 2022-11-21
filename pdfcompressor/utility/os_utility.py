import os
import re
import shutil
from types import SimpleNamespace

import jsons

from pdfcompressor.utility.console_utility import ConsoleUtility


class OsUtility:
    @classmethod
    def get_file_list(cls, folder: str, ending: str = "") -> list:
        if not os.path.exists(folder):
            raise FileNotFoundError
        if os.path.isfile(folder):
            raise ValueError
        # get all the png files in temporary folder <=> all pdf pages
        files = []
        for r, _, f in os.walk(folder):
            for file_name in f:
                if not file_name.endswith(ending):
                    continue
                files.append(os.path.join(r, file_name))
        files.sort()
        return files

    @classmethod
    def clean_up_folder(cls, folder: str) -> None:
        if os.path.isfile(folder):
            raise ValueError
        if not os.path.exists(folder):
            raise FileNotFoundError
        # removes the directory and files in 'folder'
        ConsoleUtility.print("--cleaning up--")
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    @classmethod  # todo unitTest
    def move_file(cls, from_file: str, to_file: str):
        cls.copy_file(from_file, to_file)
        os.remove(from_file)

    @classmethod  # todo unitTest
    def copy_file(cls, from_file: str, to_file: str):
        # skip copy if equals
        if from_file == to_file:
            return
        # create directory if not already exists
        output_dir = os.path.dirname(to_file)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        shutil.copy(from_file, to_file)

    @classmethod
    def get_filename(cls, full_path_to_file: str, file_ending_format: str = r"\.[^.]*$") -> str:
        filename_with_ending = os.path.basename(full_path_to_file)
        return re.split(file_ending_format, filename_with_ending)[0]

    @classmethod
    def get_filesize_list(cls, file_list: list) -> list:
        return [cls.get_file_size(file) for file in file_list]

    @classmethod
    def get_file_size(cls, file_path: str) -> int:
        """
            :returns
                0 if not an existing file
                else it returns the size of a file in bytes
        """
        if not os.path.isfile(file_path):
            return 0
        return os.stat(file_path).st_size

    @classmethod
    def get_config(cls, config_file: str = "./config.json"):
        config_path = os.path.abspath(config_file)
        if not os.path.isfile(config_path):
            raise FileNotFoundError("config file not found")

        class Config:
            def __init__(self, advpng_path, pngquant_path, pngcrush_path, cpdfsqueeze_path, tesseract_path, tessdata_prefix, wine_path):
                self.advpng_path = advpng_path
                self.pngquant_path = pngquant_path
                self.pngcrush_path = pngcrush_path
                self.cpdfsqueeze_path = cpdfsqueeze_path
                self.tesseract_path = tesseract_path
                self.tessdata_prefix = tessdata_prefix
                self.wine_path = wine_path

        with open(config_path, "r") as config_file:
            obj = jsons.loads(config_file.read(), object_hook=lambda d: SimpleNamespace(**d))
        return Config(**obj)
