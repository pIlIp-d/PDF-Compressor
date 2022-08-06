import os
from pdfcompressor.utility.os_utility import OsUtility


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
            file_ending: str = ".pdf",
            default_name_postfix: str = "_new"
    ):
        self.input_file_list = []
        self.output_file_list = []
        self.merging = False

        # fills file_list with all pdf files that are going to be compressed
        # source_path is a folder -> len(file_list) >= 0 depending on how many files are found
        if os.path.isdir(input_path):
            if output_path == "default":
                output_path = os.path.abspath(input_path) + default_name_postfix

            if os.path.isfile(output_path) or output_path.endswith(file_ending):
                # merges if more than one input file in input folder
                self.merging = True

            self.input_file_list = OsUtility.get_file_list(input_path, file_ending)
            for file in self.input_file_list:
                self.output_file_list.append(rf"{output_path}/{OsUtility.get_filename(file)}.pdf")

        # source_path is a file -> len(file_list) == 1
        else:
            if output_path == "default":
                filename_without_file_ending = input_path[:-len(file_ending)]
                output_path = os.path.abspath(filename_without_file_ending) + default_name_postfix + file_ending

            elif not output_path.endswith(file_ending):
                output_path = os.path.join(output_path, os.path.basename(input_path))

            self.input_file_list.append(input_path)
            self.output_file_list.append(output_path)

    def get_input_file_paths(self) -> list:
        return self.input_file_list

    def get_output_file_paths(self) -> list:
        return self.output_file_list

    def is_merging(self) -> bool:
        return self.merging
