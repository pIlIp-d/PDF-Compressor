import glob
import os
import shutil
from unittest import TestCase

from django_app.utility.os_utility import OsUtility
from tests.help_classes import clean_up_after_class, SimpleMergeProcessor, SimpleFakeMergeProcessor


class TestProcessorConstructorCanMerge(TestCase):

    @staticmethod
    def __get_path_variations() -> list[list[str]]:
        for variation in [
            [os.path.join(".", "TestData", "empty.txt"), os.path.join(".", "TestData", "output.txt"), False],
            [os.path.join(".", "TestData", "testFolder"), os.path.join(".", "TestData", "output.txt"), True],
            [os.path.join(".", "TestData", "empty.txt"), os.path.join(".", "TestData", "outputFolder"), False],
            [os.path.join(".", "TestData", "testFolder"), os.path.join(".", "TestData", "outputFolder"), False],
            [os.path.join(".", "TestData", "empty.txt"), "merge", True],
            [os.path.join(".", "TestData", "testFolder"), "merge", True],
            [os.path.join(".", "TestData", "empty.txt"), "default", False],
            [os.path.join(".", "TestData", "testFolder"), "default", False],
        ]:
            yield variation

    def __remove_files_if_can_merge_test_was_successful(self, source_path, destination_path):
        # remove files if processing was successful
        if destination_path not in ["merge", "default"]:
            self.assertTrue(os.path.exists(destination_path))
            if os.path.isfile(destination_path):
                os.remove(destination_path)
            else:
                shutil.rmtree(os.path.join(".", "TestData", "outputFolder"))
        else:
            result_path = self.__get_default_result_path(source_path)
            if os.path.isfile(source_path):
                os.remove(result_path)
            elif os.path.isdir(source_path):
                shutil.rmtree(result_path)

    def __get_default_result_path(self, source_path):
        if os.path.isfile(source_path):
            merged_files = glob.glob(os.path.join(".", "TestData", "*_merged_*"))
            if len(merged_files) > 0:
                return merged_files[0]
            else:
                # destination path was default
                return source_path[:-len(".txt")] + "_processed.txt"
        elif os.path.isdir(source_path):
            return source_path + "_processed"
        self.fail("no result files created")

    def test_processor_can_merge_is_true_with_merge_processor(self):
        processor = SimpleMergeProcessor(True)
        for source_path, destination_path, should_merge in self.__get_path_variations():
            processor.process(source_path, destination_path)
            if should_merge:
                merged_file = destination_path
                if destination_path == "merge":
                    # rebuild autogenerated destination path (->merged_file)
                    merged_file = self.__get_default_result_path(source_path)
                    if os.path.isdir(merged_file):
                        merged_file = OsUtility.get_file_list(merged_file)[0]
                # compare the values of all input and the merged output file
                with open(merged_file) as file:
                    merged_string = ""
                    for f_path in OsUtility.get_file_list(source_path, "txt"):
                        with open(f_path) as f:
                            merged_string += f.read()
                    self.assertEqual(merged_string, file.read())
            self.__remove_files_if_can_merge_test_was_successful(source_path, destination_path)

    def test_processor_can_merge_is_true_but_processor_doesnt_support_merge(self):
        processor = SimpleFakeMergeProcessor(True)
        for source_path, destination_path, should_merge in self.__get_path_variations():
            if should_merge or source_path.endswith("notfound.txt"):
                self.assertRaises(ValueError, processor.process, source_path, destination_path)
            else:
                processor.process(source_path, destination_path)
                self.__remove_files_if_can_merge_test_was_successful(source_path, destination_path)

    def test_processor_can_merge_is_false_with_merge_processor(self):
        processor = SimpleMergeProcessor(False)
        for source_path, destination_path, should_merge in self.__get_path_variations():
            if should_merge or source_path.endswith("notfound.txt"):
                self.assertRaises(ValueError, processor.process, source_path, destination_path)
            else:
                processor.process(source_path, destination_path)
                self.__remove_files_if_can_merge_test_was_successful(source_path, destination_path)

    def test_processor_can_merge_is_false_but_processor_doesnt_support_merge(self):
        processor = SimpleFakeMergeProcessor(False)
        for source_path, destination_path, should_merge in self.__get_path_variations():
            if should_merge or source_path.endswith("notfound.txt"):
                self.assertRaises(ValueError, processor.process, source_path, destination_path)
            else:
                processor.process(source_path, destination_path)
                self.__remove_files_if_can_merge_test_was_successful(source_path, destination_path)

    @classmethod
    def tearDownClass(cls) -> None:
        clean_up_after_class()
