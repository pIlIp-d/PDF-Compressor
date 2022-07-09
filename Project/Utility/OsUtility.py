import os
import shutil


class OsUtility:

    @staticmethod
    def get_file_list(folder, ending=".png"):
        # get all the png files in temporary folder <=> all pdf pages
        files = []
        for r, _, f in os.walk(folder):
            for fname in f:
                if not fname.endswith(ending):
                    continue
                files.append(os.path.join(r, fname))
        return files

    @staticmethod
    def clean_up_folder(folder):
        # removes the directory and files that were used in compression process
        print("--cleaning up--")
        shutil.rmtree(folder)

    @staticmethod
    def create_folder_if_not_exist(file_path):
        # TODO proper support for directories
        if not os.path.isdir(os.path.dirname(file_path)):
            # file_path is a file
            os.mkdir(os.path.dirname(file_path))
        elif file_path[-1] == "/":
            # file_path is a directory because it endswith /
            os.mkdir(file_path)

    @staticmethod
    def get_filename(full_path_to_file):
        # remove .pdf, path (only Filename)
        return full_path_to_file[:-4].split(os.path.sep)[-1]
