from unittest import TestCase

from tests.help_classes import clean_up_after_class


class TestProcessorProcess(TestCase):
    def test_todo(self):
        self.fail("nothing implemented yet")  # TODO

    @classmethod
    def tearDownClass(cls) -> None:
        clean_up_after_class()

# TODO
# ProcessorWithDestinationFolder
#   from folder
#   to file
#   wrong implementation of _process_file_list (unequal amount of source, destination paths)
#   from folder with only one file
#   source path doesn't exist

# AbstractPdfProcessor


# Plugin Classes


# Django Views / Selenium

# Task Scheduler
