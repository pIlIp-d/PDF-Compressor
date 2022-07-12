import os
import re
import shutil

from pdfcompressor.utility.ConsoleUtility import ConsoleUtility


class OsUtility:
    @staticmethod
    def get_file_list(folder: str, ending: str = "") -> list:
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
        return files

    @staticmethod
    def clean_up_folder(folder: str) -> None:
        if os.path.isfile(folder):
            raise ValueError
        if not os.path.exists(folder):
            raise FileNotFoundError
        # removes the directory and files in 'folder'
        ConsoleUtility.print("--cleaning up--")
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    @staticmethod
    def get_filename(full_path_to_file: str, file_ending_format: str = r"\..*") -> str:
        filename_with_ending = os.path.basename(full_path_to_file)
        return re.split(file_ending_format, filename_with_ending)[0]
