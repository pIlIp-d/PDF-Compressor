from unittest import TestCase

from tests.help_classes import clean_up_after_class


class TestProcessorProcess(TestCase):
    def test_todo(self):
        self.fail("nothing implemented yet")  # TODO

    @classmethod
    def tearDownClass(cls) -> None:
        clean_up_after_class()
