import os.path
from unittest import TestCase

from django_app.plugin_system.processing_classes.processor import Processor
from django_app.utility.os_utility import OsUtility
from tests.help_classes import clean_up_after_class, simple_copy_process_file, simple_merge_files, \
    DestinationFolderSubClass


class ProcessTestProcessor(Processor):
    def __init__(self, **kwargs):
        super().__init__([], ["txt"], "txt", **kwargs)

    def process_file(self, source_file: str, destination_path: str) -> None:
        simple_copy_process_file(self, source_file, destination_path)

    def _merge_files(self, file_list: list[str], merged_result_file: str) -> None:
        simple_merge_files(self, file_list, merged_result_file)


class ProcessTestCase(TestCase):
    @classmethod
    def _remove_if_exists(cls, destination):
        exists = os.path.isfile(destination)
        if exists:
            os.remove(destination)
        return exists

    @classmethod
    def _run_process(cls, source_path: str, destination_path: str, **kwargs):
        processor = ProcessTestProcessor(**kwargs)
        processor.process(source_path, destination_path)

    @classmethod
    def _get_file_content_and_remove_file(cls, path: str):
        result_content = cls._get_file_content(path)
        if os.path.exists(path):
            os.remove(path)
        return result_content

    @classmethod
    def _get_file_content(cls, path: str):
        result_content = ""
        if os.path.isfile(path):
            with open(path, "r") as f:
                result_content = f.read()
        return result_content

    def _run_test_processing_to_destination_folder(self, source_path: str,
                                                   destination_folder: str = "./TestData/resultFolder", **kwargs):
        self._run_process(source_path, destination_folder, **kwargs)
        # check if for each source file a destination file has been created
        source_files = OsUtility.get_file_list(source_path, ".txt")
        results: list[bool] = list()
        for file in source_files:
            destination_file = os.path.join(destination_folder, os.path.basename(file))
            results.append(self._remove_if_exists(destination_file))
        os.removedirs(destination_folder)
        for result in results:
            self.assertTrue(result)

    def _run_test_processing_to_destination_file(self, source_path: str, destination_file: str, **kwargs):
        self._run_process(source_path, destination_file, **kwargs)
        self.assertTrue(os.path.exists(destination_file))
        os.remove(destination_file)


class TestProcessorProcess(ProcessTestCase):
    def test_valid_relative_input_file(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt")

    def test_valid_relative_input_folder(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolder")

    def test_valid_absolute_input_file(self):
        self._run_test_processing_to_destination_folder(os.path.abspath("./TestData/testFile.txt"))

    def test_valid_absolute_input_folder(self):
        self._run_test_processing_to_destination_folder(os.path.abspath("./TestData/testFolder"))

    def test_valid_empty_input_folder(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_folder,
            os.path.abspath("./TestData/emptyFolder")
        )

    def test_valid_input_folder_with_slash_at_the_end(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolder/")

    def test_valid_input_folder_that_looks_like_file(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolderLooksLikeFile.txt")

    def test_valid_input_file_with_spaces(self):
        self._run_test_processing_to_destination_folder("./TestData/test File with space.txt")

    def test_valid_input_file_with_special_chars(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile_+-special_Chars.txt")

    def test_invalid_input_file_doesnt_exist(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_folder,
            "./TestData/noFile.txt"
        )

    def test_invalid_input_folder_doesnt_exist(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_folder,
            "./TestData/noFolder.txt"
        )

    def test_invalid_input_folder_with_not_allowed_special_chars(self):
        if os.name == "nt":
            not_allowed_chars = "#%<>$+`|=!’”:@/?*&{}\\"  # TODO update list to only contain forbidden characters
            for char in not_allowed_chars:
                self.assertRaises(
                    ValueError,
                    self._run_test_processing_to_destination_folder,
                    "./TestData/filename" + char
                )
        else:
            self.fail("IGNORED: This test is only for windows.")

    def test_valid_input_path_without_path_indication_at_start(self):
        self._run_test_processing_to_destination_folder("TestData/testFile.txt")

    def test_invalid_input_path_file_type(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_folder,
            "TestData/testFile.pdf"
        )

    def test_invalid_input_path_is_empty_string(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_folder,
            ""
        )

    def test_valid_input_folder_with_only_one_file_and_with_can_merge(self):
        self._run_test_processing_to_destination_file("./TestData/testFolderWithOneFile", "TestData/resultFile.txt",
                                                      can_merge=True)

    def test_valid_input_folder_with_only_one_file_and_without_can_merge(self):
        self._run_test_processing_to_destination_file("./TestData/testFolderWithOneFile", "TestData/resultFile.txt",
                                                      can_merge=False)

    def test_valid_destination_file_already_exists(self):
        source_file = "TestData/testFile.txt"
        destination_file = "./TestData/existingFile.txt"
        # create empty destination_file
        open(destination_file, "w").close()
        self._run_process(source_file, destination_file)
        # compare file content
        self.assertEqual(self._get_file_content(source_file),
                         self._get_file_content_and_remove_file(destination_file))

    def test_valid_destination_folder_already_exists(self):
        destination_folder = "./TestData/existingFolder"
        os.makedirs(destination_folder, exist_ok=True)
        self._run_test_processing_to_destination_folder("TestData/testFile.txt", destination_folder)

    def test_valid_destination_folder_with_some_files_already_exist(self):
        source_folder = "TestData/testFolder"
        destination_folder = "./TestData/existingFilledFolder"
        os.makedirs(destination_folder, exist_ok=True)

        source_files = OsUtility.get_file_list(source_folder, ".txt")
        # create some empty files with same names as in input dir
        for file_id, file in enumerate(source_files):
            if file_id % 2 == 0:
                open(os.path.join(destination_folder, os.path.basename(file)), "w").close()

        self._run_process(source_folder, destination_folder)
        # compare file content
        for source_file, destination_file in zip(
                OsUtility.get_file_list(source_folder, "txt"), OsUtility.get_file_list(destination_folder, "txt")):
            # compare file content
            self.assertEqual(self._get_file_content(source_file),
                             self._get_file_content_and_remove_file(destination_file))
        os.removedirs(destination_folder)

    def test_valid_destination_folder_with_some_extra_files_exist(self):
        source_folder = "TestData/testFolder"
        destination_folder = "./TestData/existingExtraFilledFolder"
        os.makedirs(destination_folder, exist_ok=True)

        # create extra files
        extra_files = [os.path.join(destination_folder, "extraFile_0235.md"),
                       os.path.join(destination_folder, "extraFile_0235.txt")]
        for file in extra_files:
            open(file, "w").close()

        self._run_process(source_folder, destination_folder)
        # check, remove extra files and processed source files
        for file in extra_files + [os.path.join(destination_folder, os.path.basename(file)) for file in
                                   OsUtility.get_file_list(source_folder, "txt")]:
            self.assertTrue(os.path.isfile(file))
            os.remove(file)
        os.removedirs(destination_folder)

    def test_valid_destination_file_relative_path(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt", "./TestData/resultFile.txt")

    def test_valid_destination_folder_relative_path(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt")

    def test_valid_destination_file_absolute_path(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt",
                                                      os.path.abspath("./TestData/resultFile.txt"))

    def test_valid_destination_folder_absolute_path(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt",
                                                        os.path.abspath("./TestData/resultFolder"))

    def test_valid_destination_folder_looks_like_file(self):
        destination_folder = "./TestData/resultFolderLikeFile.txt"
        if os.path.isfile(destination_folder):
            os.remove(destination_folder)
        os.makedirs(destination_folder, exist_ok=True)
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt", destination_folder)
        os.makedirs(destination_folder, exist_ok=True)
        self._run_test_processing_to_destination_folder("./TestData/testFolder", destination_folder, can_merge=True)

    def test_valid_destination_path_with_special_chars(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt",
                                                      "./TestData/resultFile_+-special_Chars.txt")

    def test_valid_destination_path_with_space(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt", "./ TestData / result File.txt")

    def test_invalid_destination_path_with_not_allowed_special_chars(self):
        if os.name == "nt":
            not_allowed_chars = "#%<>$+`|=!’”:@/?*&{}\\"  # TODO update list to only contain forbidden characters
            for char in not_allowed_chars:
                self.assertRaises(
                    ValueError,
                    self._run_test_processing_to_destination_file,
                    "./TestData/testFile.txt",
                    "./TestData/filename%s.txt" % char
                )
        else:
            self.fail("IGNORED: This test is only for windows.")

    def test_valid_destination_path_without_path_indication_at_start(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt", "TestData/resultFile.txt")

    def test_invalid_destination_path_file_type(self):
        self.assertRaises(
            IsADirectoryError,
            self._run_test_processing_to_destination_file,
            "./TestData/testFile.txt", "TestData/resultFile.pdf"
        )
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt", "TestData/resultFile.pdf")

    def test_invalid_destination_path_is_empty_string(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_file,
            "./TestData/testFile.txt", ""
        )

    def test_valid_output_file_from_input_file(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt", "TestData/resultFile.txt")

    def test_valid_output_file_from_input_folder_with_can_merge(self):
        self._run_test_processing_to_destination_file("./TestData/testFolder", "TestData/resultFile.txt",
                                                      can_merge=True)

    def test_invalid_output_file_from_input_folder_without_can_merge(self):
        self.assertRaises(
            ValueError,
            self._run_test_processing_to_destination_file,
            "./TestData/testFolder", "TestData/resultFile.txt",
            can_merge=False
        )

    def test_valid_output_folder_from_input_file(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt", "./TestData/resultFolder")

    def test_valid_output_folder_from_input_folder(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolder", "./TestData/resultFolder")

    @classmethod
    def tearDownClass(cls) -> None:
        clean_up_after_class()


class TestProcessorWithDestinationFolderProcess(ProcessTestCase):
    @classmethod
    def _run_process(cls, source_path: str, destination_path: str, **kwargs):
        processor = DestinationFolderSubClass(**kwargs)
        processor.process(source_path, destination_path)

    def test_valid_input_folder_that_looks_like_file(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolderLooksLikeFile.txt")

    def test_valid_input_file(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt")

    def test_valid_input_folder(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolder")

    def test_valid_output_folder_that_looks_like_file(self):
        destination = "./TestData/resultFolderLikeFile.txt"
        os.makedirs(destination, exist_ok=True)
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt", destination)

    def test_invalid_output_path_is_empty_string(self):
        self.assertRaises(
            FileNotFoundError,
            self._run_test_processing_to_destination_file,
            "./TestData/testFile.txt", ""
        )

    def test_valid_output_file_from_input_file(self):
        self._run_test_processing_to_destination_file("./TestData/testFile.txt", "./TestData/resultFile.txt",
                                                      can_merge=True)

    def test_valid_output_file_from_input_folder_with_can_merge(self):
        self._run_test_processing_to_destination_file("./TestData/testFolder", "./TestData/resultFile.txt",
                                                      can_merge=True)

    def test_invalid_output_file_from_input_folder_without_can_merge(self):
        self.assertRaises(
            ValueError,
            self._run_test_processing_to_destination_file,
            "./TestData/testFolder", "./TestData/resultFile.txt", can_merge=False
        )

    def test_valid_output_folder_from_input_file(self):
        self._run_test_processing_to_destination_folder("./TestData/testFile.txt", "./TestData/resultFolder")

    def test_valid_output_folder_from_input_folder_with_can_merge(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolder", "./TestData/resultFolder",
                                                        can_merge=True)

    def test_valid_output_folder_from_input_folder_without_can_merge(self):
        self._run_test_processing_to_destination_folder("./TestData/testFolder", "./TestData/resultFolder",
                                                        can_merge=False)

    # TODO
    # ProcessorWithDestinationFolder

    # AbstractPdfProcessor
