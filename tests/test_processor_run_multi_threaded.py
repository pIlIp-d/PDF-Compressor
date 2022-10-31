import os
import shutil
import time
from unittest import TestCase

from django_app.utility.os_utility import OsUtility
from tests.help_classes import clean_up_after_class, SimpleMultiThreadTestProcessor
from tests.test_processor import TestingEventHandler
from tests.test_processor import ns as test_processor_ns


class TestProcessorConstructorRunMultiThreaded(TestCase):

    def __run_processing_for_many_files(self, multi_threaded: bool) -> float:
        # create Test Data
        source_folder = os.path.join(".", "TestData", "manyFiles")
        if os.path.isdir(source_folder):
            shutil.rmtree(source_folder)
        os.makedirs(source_folder)
        for i in range(100):
            with open(os.path.join(source_folder, str(i) + ".txt"), "w+") as f:
                f.write(str(i))
        destination_folder = os.path.join(".", "TestData", "outputFiles")
        start_time = time.time()
        SimpleMultiThreadTestProcessor(
            [TestingEventHandler()], multi_threaded
        ).process(source_folder, destination_folder)
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

    @classmethod
    def tearDownClass(cls) -> None:
        clean_up_after_class()
