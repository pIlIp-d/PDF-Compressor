import multiprocessing
import os
import shutil
from glob import glob
from unittest import TestCase

from tests.help_classes import SimpleProcessorForFileTypes, clean_up_after_class, TESTDATA_DIR

manager = multiprocessing.Manager()
ns = manager.Namespace()
lock = manager.Lock()


class TestProcessorConstructorFileTypes(TestCase):

    def __execute_processor(
            self,
            file_type_from=None, file_type_to: str = "txt", amount_of_result_files: int = 2, source_path: str = None
    ):
        if file_type_from is None:
            file_type_from = ["txt"]
        if source_path is None:
            source_path = os.path.join(TESTDATA_DIR, "testFolder")
        destination_path = os.path.join(TESTDATA_DIR, "outputFolder")
        SimpleProcessorForFileTypes(
            file_type_from, file_type_to
        ).process(source_path, destination_path)
        counted_output_files = len(glob(os.path.join(destination_path, "*")))
        if os.path.isfile(destination_path):
            os.remove(destination_path)
        elif os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        else:
            self.fail("no result file found")
        self.assertEqual(amount_of_result_files, counted_output_files)

    def test_processor_with_file_from_type_is_empty_list(self):
        self.assertRaises(FileNotFoundError, self.__execute_processor, file_type_from=[])

    def test_processor_with_file_from_type_is_list_of_empty_string(self):
        self.__execute_processor(file_type_from=[""], amount_of_result_files=3)

    def test_processor_with_file_from_type_is_single_valid_value(self):
        self.__execute_processor(file_type_from=["txt"])

    def test_processor_with_file_from_type_are_multiple_valid_values(self):
        self.__execute_processor(file_type_from=["txt", "md"], amount_of_result_files=3)

    def test_processor_with_file_from_type_is_single_invalid_value(self):
        self.assertRaises(FileNotFoundError, self.__execute_processor, file_type_from=["pdf"])

    def test_processor_with_file_from_type_are_multiple_invalid_values(self):
        self.assertRaises(FileNotFoundError, self.__execute_processor, file_type_from=["png", "pdf"])

    def test_processor_with_file_from_type_are_mixed_valid_and_invalid_values(self):
        self.__execute_processor(file_type_from=["md", "png"], amount_of_result_files=1)

    def test_processor_with_file_from_type_are_duplicate_valid_values(self):
        self.__execute_processor(file_type_from=["md", "md"], amount_of_result_files=1)

    def test_processor_with_file_from_type_and_multiple_file_found(self):
        self.__execute_processor(file_type_from=["txt"], amount_of_result_files=2)

    def test_processor_with_file_from_type_and_no_file_found(self):
        self.assertRaises(
            FileNotFoundError,
            self.__execute_processor,
            file_type_from=["md"],
            amount_of_result_files=0,
            source_path=os.path.join(TESTDATA_DIR, "empty.txt")
        )

    def test_process_file_type_to_is_empty_string(self):
        self.assertRaises(ValueError, self.__execute_processor, file_type_to="")

    def test_process_file_type_to_is_invalid_string(self):
        self.assertRaises(ValueError, self.__execute_processor, file_type_to="pdf")

    def test_process_file_type_to_is_valid_string(self):
        self.__execute_processor(file_type_to="txt")

    @classmethod
    def tearDownClass(cls) -> None:
        clean_up_after_class()
