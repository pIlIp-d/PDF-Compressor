import os
import shutil
import time
from unittest import TestCase

from django_app.utility.os_utility import OsUtility
from tests.help_classes import clean_up_after_class, SimpleMultiThreadTestProcessor
from tests.test_processor import TestingEventHandler
from tests.test_processor import ns as test_processor_ns


class TestProcessorConstructorRunMultiThreaded(TestCase):
    source_folder = os.path.join(".", "TestData", "manyFiles")

    def __run_processing_for_many_files(self, multi_threaded: bool) -> float:
        # create Test Data
        if os.path.isdir(self.source_folder):
            shutil.rmtree(self.source_folder)
        os.makedirs(self.source_folder)
        for i in range(100):
            with open(os.path.join(self.source_folder, str(i) + ".txt"), "w+") as f:
                f.write(str(i))
        destination_folder = os.path.join(".", "TestData", "outputFiles")
        start_time = time.time()
        SimpleMultiThreadTestProcessor(
            [TestingEventHandler()], multi_threaded
        ).process(self.source_folder, destination_folder)
        self.assertEqual(100, test_processor_ns.amount_of_postprocess_calls)
        self.assertEqual(100, len(OsUtility.get_file_list(destination_folder)))
        elapsed_time = time.time() - start_time
        # cleanup
        shutil.rmtree(destination_folder)
        return elapsed_time

    def test_many_files_with_run_multi_threaded(self):
        self.__run_processing_for_many_files(True)

    def test_many_files_without_run_multi_threaded(self):
        self.__run_processing_for_many_files(False)

    def test_run_and_compare_multi_threaded_executions(self):
        self.assertTrue(self.__run_processing_for_many_files(True) < self.__run_processing_for_many_files(False))

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.source_folder)
        clean_up_after_class()
