import os
import shutil
import multiprocessing
from unittest import TestCase

from django_app.plugin_system.processing_classes.event_handler import EventHandler
from django_app.plugin_system.processing_classes.processor import Processor
from django_app.plugin_system.processing_classes.processorwithdestinationfolder import ProcessorWithDestinationFolder


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
        self.amount_of_started_processing_calls = 0
        self.amount_of_finished_all_files_calls = 0
        self.amount_of_preprocess_calls = 0
        self.amount_of_postprocess_calls = 0

    def started_processing(self):
        self.amount_of_started_processing_calls += 1

    def finished_all_files(self):
        self.amount_of_finished_all_files_calls += 1

    def preprocess(self, source_file: str, destination_file: str) -> None:
        self.amount_of_preprocess_calls = 0

    def postprocess(self, source_file: str, destination_file: str) -> None:
        self.amount_of_postprocess_calls = 0


class TestProcessor(TestCase):
    def get_amount_of_calls(
            self,
            source_path: str,
            destination_path: str,
            amount_of_event_handlers: int = 1
    ) -> TestingEventHandler:
        event_handler = TestingEventHandler()
        SimpleExampleProcessor([event_handler for _ in range(amount_of_event_handlers)], "txt", "txt").process(
            source_path, destination_path
        )
        if os.path.isfile(destination_path):
            os.remove(destination_path)
        elif os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        else:
            self.fail("no result created")
        return event_handler

    def test_started_processed_with_single_file(self):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "result.txt")
        self.assertEqual(1, self.get_amount_of_calls(source_path, destination_path).amount_of_started_processing_calls)

    def test_started_processed_with_multiple_files(self):
        source_path = os.path.join(".", "TestData", "testFolder")
        destination_path = os.path.join(".", "TestData", "testOutput")
        self.assertEqual(1, self.get_amount_of_calls(source_path, destination_path).amount_of_started_processing_calls)

    def test_started_processed_with_no_files(self):
        source_path = os.path.join(".", "TestData", "emptyFolder")
        destination_path = os.path.join(".", "TestData", "testOutput")
        self.assertRaises(
            ValueError,
            self.get_amount_of_calls,
            source_path, destination_path
        )

    def test_started_processed_with_two_event_handlers(self):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "result.txt")
        self.assertEqual(
            2, self.get_amount_of_calls(source_path, destination_path, 2).amount_of_started_processing_calls
        )

    def test_started_processed_with_no_event_handler(self):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "result.txt")
        self.assertEqual(
            0, self.get_amount_of_calls(source_path, destination_path, 0).amount_of_started_processing_calls
        )

    def test_started_processed_with_error_while_processing(self):
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "result.txt")
        event_handler = TestingEventHandler()
        processor = ErrorProcessor([event_handler], "txt", "txt")
        self.assertRaises(
            FailedProcessingException,
            processor.process,
            source_path,
            destination_path
        )
        self.assertEqual(1, event_handler.amount_of_started_processing_calls)

    def test_started_processed_with_processor_is_processor_with_destination_folder_instance(self):
        event_handler = TestingEventHandler()
        processor = DestinationFolderSubClass([event_handler], "txt", "txt")
        source_path = os.path.join(".", "TestData", "empty.txt")
        destination_path = os.path.join(".", "TestData", "outputFolder")
        processor.process(source_path, destination_path)
        self.assertEqual(1, event_handler.amount_of_started_processing_calls)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(os.path.join(".", "temporary_files"))
