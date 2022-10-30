import os
import shutil
import multiprocessing
from unittest import TestCase

from django_app.plugin_system.processing_classes.event_handler import EventHandler
from django_app.plugin_system.processing_classes.processor import Processor
from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder

manager = multiprocessing.Manager()
ns = manager.Namespace()
lock = manager.Lock()


class SimpleExampleProcessor(Processor):
    def __init__(self, event_handler: [EventHandler], file_type_from: str, file_type_to: str):
        super().__init__(event_handler, file_type_from, file_type_to)

    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


class FailedProcessingException(Exception):
    pass


class ErrorProcessor(Processor):
    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        raise FailedProcessingException
        self.postprocess(source_file, destination_path)


class DestinationFolderSubClass(ProcessorWithDestinationFolder):
    def process_file(self, source_file: str, destination_path: str) -> None:
        self.preprocess(source_file, destination_path)
        shutil.copyfile(source_file, destination_path)
        self.postprocess(source_file, destination_path)


class TestingEventHandler(EventHandler):
    def __init__(self):
        ns.amount_of_started_processing_calls = 0
        ns.amount_of_finished_all_files_calls = 0
        ns.amount_of_preprocess_calls = 0
        ns.amount_of_postprocess_calls = 0

    def started_processing(self):
        with lock:
            ns.amount_of_started_processing_calls += 1

    def finished_all_files(self):
        with lock:
            ns.amount_of_finished_all_files_calls += 1

    def preprocess(self, source_file: str, destination_file: str) -> None:
        with lock:
            ns.amount_of_preprocess_calls += 1

    def postprocess(self, source_file: str, destination_file: str) -> None:
        with lock:
            ns.amount_of_postprocess_calls += 1


class TestProcessor(TestCase):
    def __execute_monitored_processing(
            self,
            source_path: str,
            destination_path: str,
            amount_of_event_handlers: int,
            processor_class
    ) -> None:
        event_handler = TestingEventHandler()
        processor_class([event_handler for _ in range(amount_of_event_handlers)], "txt", "txt").process(
            source_path, destination_path
        )
        if os.path.isfile(destination_path):
            os.remove(destination_path)
        elif os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        else:
            self.fail("no result created")

    def __execute_simple_processing_from_file(self, amount_of_event_handlers: int = 1):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "result.txt")
        self.__execute_monitored_processing(
            source_path, destination_path, amount_of_event_handlers, SimpleExampleProcessor
        )

    def __execute_simple_processing_from_folder(
            self, amount_of_event_handlers: int = 1, source_folder: str = os.path.join(".", "TestData", "testFolder")
    ):
        destination_path = os.path.join(".", "TestData", "testOutput")
        self.__execute_monitored_processing(
            source_folder, destination_path, amount_of_event_handlers, SimpleExampleProcessor
        )

    def __execute_monitored_error_processor(self):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "result.txt")
        self.__execute_monitored_processing(source_path, destination_path, 1, ErrorProcessor)

    def __execute_monitored_processor_with_destination_folder_sub_class(self):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "outputFolder")
        self.__execute_monitored_processing(source_path, destination_path, 1, DestinationFolderSubClass)

    def test_started_processed_with_single_file(self):
        self.__execute_simple_processing_from_file()
        self.assertEqual(1, ns.amount_of_started_processing_calls)

    def test_started_processed_with_multiple_files(self):
        self.__execute_simple_processing_from_folder()
        self.assertEqual(1, ns.amount_of_started_processing_calls)

    def test_started_processed_with_no_files(self):
        self.assertRaises(
            ValueError, self.__execute_simple_processing_from_folder,
            source_folder=os.path.join(".", "TestData", "emptyFolder")
        )
        self.assertEqual(0, ns.amount_of_started_processing_calls)

    def test_started_processed_with_two_event_handlers(self):
        self.__execute_simple_processing_from_file(2)
        self.assertEqual(2, ns.amount_of_started_processing_calls)

    def test_started_processed_with_no_event_handler(self):
        self.__execute_simple_processing_from_file(0)
        self.assertEqual(0, ns.amount_of_started_processing_calls)

    def test_started_processed_with_error_while_processing(self):
        self.assertRaises(FailedProcessingException, self.__execute_monitored_error_processor)
        self.assertEqual(1, ns.amount_of_started_processing_calls)

    def test_started_processed_with_processor_is_processor_with_destination_folder_instance(self):
        self.__execute_monitored_processor_with_destination_folder_sub_class()
        self.assertEqual(1, ns.amount_of_started_processing_calls)

    def test_finished_all_files_with_single_file(self):
        self.__execute_simple_processing_from_file()
        self.assertEqual(1, ns.amount_of_finished_all_files_calls)

    def test_finished_all_files_with_multiple_files(self):
        self.__execute_simple_processing_from_folder()
        self.assertEqual(1, ns.amount_of_finished_all_files_calls)

    def test_finished_all_files_with_no_files(self):
        self.assertRaises(
            ValueError, self.__execute_simple_processing_from_folder,
            source_folder=os.path.join(".", "TestData", "emptyFolder")
        )
        self.assertEqual(0, ns.amount_of_finished_all_files_calls)

    def test_finished_all_files_with_two_event_handlers(self):
        self.__execute_simple_processing_from_file(2)
        self.assertEqual(2, ns.amount_of_finished_all_files_calls)

    def test_finished_all_files_with_no_event_handler(self):
        self.__execute_simple_processing_from_file(0)
        self.assertEqual(0, ns.amount_of_finished_all_files_calls)

    def test_finished_all_files_with_error_while_processing(self):
        self.assertRaises(FailedProcessingException, self.__execute_monitored_error_processor)
        self.assertEqual(0, ns.amount_of_finished_all_files_calls)

    def test_finished_all_files_with_processor_is_processor_with_destination_folder_instance(self):
        self.__execute_monitored_processor_with_destination_folder_sub_class()
        self.assertEqual(1, ns.amount_of_finished_all_files_calls)

    def test_preprocess_with_single_file(self):
        self.__execute_simple_processing_from_file()
        self.assertEqual(1, ns.amount_of_preprocess_calls)

    def test_preprocess_with_multiple_files(self):
        self.__execute_simple_processing_from_folder()
        self.assertEqual(2, ns.amount_of_preprocess_calls)

    def test_preprocess_with_no_files(self):
        self.assertRaises(
            ValueError, self.__execute_simple_processing_from_folder,
            source_folder=os.path.join(".", "TestData", "emptyFolder")
        )
        self.assertEqual(0, ns.amount_of_preprocess_calls)

    def test_preprocess_with_two_event_handlers(self):
        self.__execute_simple_processing_from_file(2)
        self.assertEqual(2, ns.amount_of_preprocess_calls)

    def test_preprocess_with_no_event_handler(self):
        self.__execute_simple_processing_from_file(0)
        self.assertEqual(0, ns.amount_of_preprocess_calls)

    def test_preprocess_with_error_while_processing(self):
        self.assertRaises(FailedProcessingException, self.__execute_monitored_error_processor)
        self.assertEqual(1, ns.amount_of_preprocess_calls)

    def test_preprocess_with_processor_is_processor_with_destination_folder_instance(self):
        self.__execute_monitored_processor_with_destination_folder_sub_class()
        self.assertEqual(1, ns.amount_of_finished_all_files_calls)

    def test_postprocess_with_single_file(self):
        self.__execute_simple_processing_from_file()
        self.assertEqual(1, ns.amount_of_postprocess_calls)

    def test_postprocess_with_multiple_files(self):
        self.__execute_simple_processing_from_folder()
        self.assertEqual(2, ns.amount_of_postprocess_calls)

    def test_postprocess_with_no_files(self):
        self.assertRaises(
            ValueError, self.__execute_simple_processing_from_folder,
            source_folder=os.path.join(".", "TestData", "emptyFolder")
        )
        self.assertEqual(0, ns.amount_of_postprocess_calls)

    def test_postprocess_with_two_event_handlers(self):
        self.__execute_simple_processing_from_file(2)
        self.assertEqual(2, ns.amount_of_postprocess_calls)

    def test_postprocess_with_no_event_handler(self):
        self.__execute_simple_processing_from_file(0)
        self.assertEqual(0, ns.amount_of_postprocess_calls)

    def test_postprocess_with_error_while_processing(self):
        self.assertRaises(FailedProcessingException, self.__execute_monitored_error_processor)
        self.assertEqual(0, ns.amount_of_postprocess_calls)

    def test_postprocess_with_processor_is_processor_with_destination_folder_instance(self):
        self.__execute_monitored_processor_with_destination_folder_sub_class()
        self.assertEqual(1, ns.amount_of_postprocess_calls)

    @classmethod
    def tearDownClass(cls) -> None:
        temp_dir = os.path.join(".", "temporary_files")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
