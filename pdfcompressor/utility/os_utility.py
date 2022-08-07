import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    @classmethod  # todo unitTest
    def get_file_size(cls, file_path: str) -> int:
        if not os.path.exists(file_path):
            return 0
        return os.stat(file_path).st_size

    @classmethod  # TODO unitTesting
    def custom_map_execute(cls, method, args_list: list):
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            tasks = []
            for method_parameter in args_list:
                tasks.append(executor.submit(method, **method_parameter))
            # waits for all jobs to be completed
            for _ in as_completed(tasks):
                pass