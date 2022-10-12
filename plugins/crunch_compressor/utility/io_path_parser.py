import os
from plugins.crunch_compressor.utility.os_utility import OsUtility
# TODO unittest paths with this class -> improves performance of tests extremely


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
            file_ending_source: str = "",
            file_ending_dest: str = "",
            default_name_postfix: str = "_new"
    ):
        """
        :param file_ending_source: if empty and input_path is a directory
               all files in the source directory are accepted, which may ends in error while processing,
               when it contains unsupported file types
        """
        self.__input_path = os.path.abspath(input_path)
        self.__default_output = output_path == "default"
        self.__output_path = os.path.abspath(output_path)
        self.__file_ending_source = file_ending_source.lower()
        if file_ending_dest == "":
            raise ValueError("file_ending_dest can't be empty. ")
        self.__file_ending_dest = file_ending_dest.lower()
        self.__default_name_postfix = default_name_postfix
        self.__input_file_list = []
        self.__output_file_list = []
        self.__is_merger = False

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

        if len(self.__input_file_list) > 1 and self.__is_file(self.__output_path, self.__file_ending_dest):
            self.__is_merger = True

        for file in self.__input_file_list:
            self.__output_file_list.append(
                os.path.join(self.__output_path, OsUtility.get_filename(file) + "." + self.__file_ending_dest)
            )

    def __parse_from_input_file(self):
        # file ending plus '.'
        input_path_without_file_ending = OsUtility.get_path_without_file_ending(self.__input_path) + "."

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
        return self.__is_merger
