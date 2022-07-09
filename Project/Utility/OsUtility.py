import os
import shutil


class OsUtility:

    @staticmethod
    def get_file_list(folder, ending=".png") -> list:
        # get all the png files in temporary folder <=> all pdf pages
        files = []
        for r, _, f in os.walk(folder):
            for fname in f:
                if not fname.endswith(ending):
                    continue
                files.append(os.path.join(r, fname))
        return files

    @staticmethod
    def clean_up_folder(folder) -> None:
        # removes the directory and files that were used in compression process
        print("--cleaning up--")
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    @staticmethod
    def create_folder_if_not_exist(file_path) -> None:
        # checks if .pdf file else creates folder if there is no folder, yet
        if not file_path.endswith(".pdf") and not os.path.isdir(file_path):
            os.mkdir(file_path)
        elif not os.path.isdir(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))

    @staticmethod
    def get_filename(full_path_to_file) -> str:
        # remove .pdf, path (only Filename)
        return full_path_to_file[:-4].split(os.path.sep)[-1]
