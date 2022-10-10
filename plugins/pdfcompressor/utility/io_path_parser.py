import os
from plugins.pdfcompressor.utility.os_utility import OsUtility
# test paths with this class -> improves performance of tests extremely


class IOPathParser:
    # Cases
    # File -> File
    # File -> Folder
    # Folder -> Folder
    # Folder -> File
    def __init__(
            self,
            input_path: str,
            output_path: str = "default",
            file_ending_source: str = ".pdf",
            file_ending_dest: str = ".pdf",
            default_name_postfix: str = "_new"
    ):
        self.__input_path = os.path.abspath(input_path)
        self.__default_output = output_path == "default"
        self.__output_path = os.path.abspath(output_path)
        self.__file_ending_source = file_ending_source
        self.__file_ending_dest = file_ending_dest
        self.__default_name_postfix = default_name_postfix
        self.__input_file_list = []
        self.__output_file_list = []

        if self.__is_dir(input_path):
            self.__parse_from_input_folder()
        else:
            self.__parse_from_input_file()

        self.__input_file_list.sort()
        self.__output_file_list.sort()

    def __is_dir(self, path: str) -> bool:
        return os.path.isdir(path) or not path.endswith(self.__file_ending_source)

    @classmethod
    def __is_file(cls, path: str, ending: str) -> bool:
        return path.endswith(ending)

    def __parse_from_input_folder(self):
        self.__input_file_list = OsUtility.get_file_list(self.__input_path, self.__file_ending_source)

        if self.__default_output:
            self.__output_path = self.__input_path + self.__default_name_postfix

        if self.__is_file(self.__output_path, self.__file_ending_dest):
            self.__output_file_list.append(self.__output_path)
        else:
            for file in self.__input_file_list:
                self.__output_file_list.append(
                    os.path.join(self.__output_path, OsUtility.get_filename(file) + self.__file_ending_dest)
                )

    def __parse_from_input_file(self):
        input_path_without_file_ending = self.__input_path[:-len(self.__file_ending_source)]

        if self.__default_output:
            output_path = input_path_without_file_ending + self.__default_name_postfix + self.__file_ending_dest
        elif not self.__is_file(self.__output_path, self.__file_ending_dest):
            output_path = os.path.join(self.__output_path, os.path.basename(input_path_without_file_ending))
        else:
            output_path = self.__output_path

        self.__input_file_list.append(self.__input_path)
        self.__output_file_list.append(output_path)

    def get_input_file_paths(self) -> list:
        return self.__input_file_list

    def get_output_file_paths(self) -> list:
        return self.__output_file_list

    def is_merging(self) -> bool:
        return len(self.__input_file_list) > len(self.__output_file_list) == 1
