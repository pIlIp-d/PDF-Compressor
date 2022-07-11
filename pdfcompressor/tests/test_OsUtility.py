import os.path
import shutil
from unittest import TestCase

from pdfcompressor.utility.OsUtility import OsUtility


class TestOsUtility(TestCase):
    test_filename = os.path.abspath("./testFolder/test.file")

    def test_get_file_list(self):
        self.fail("Not Implemented Yet")

    def test_clean_up_folder(self):
        self.fail("Not Implemented Yet")

    def test_create_folder_if_not_exist(self):
        # folder doesn't exists
        self.assertFalse(os.path.isdir(os.path.dirname(self.test_filename)))

        OsUtility.create_folder_if_not_exist(self.test_filename)

        # folder exists
        self.assertTrue(os.path.isdir(os.path.dirname(self.test_filename)))
        os.rmdir(os.path.dirname(self.test_filename))

    def test_get_filename(self):  # TODO more TestCases
        self.assertEquals("singlePagePdf", OsUtility.get_filename(os.path.abspath("TestData/single Page Pdf.pdf")))

    def tearDown(self):
        if os.path.isdir(self.test_filename):
            shutil.rmtree(self.test_filename)
