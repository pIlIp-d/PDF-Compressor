import os.path
import shutil
import subprocess
import sys
from io import StringIO
from unittest import TestCase

from pdfcompressor.utility.OsUtility import OsUtility


class TestConsolePDFCompressor(TestCase):
    def remove_if_not_exists(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_compress_single_file(self):
        result_path = './TestData/multiPageTestData_compressed.pdf'
        self.remove_if_not_exists(result_path)
        subprocess.call(["python3", os.path.abspath('../pdfcompressor.py'),
                         "-p", os.path.abspath('./TestData/multiPageTestData.pdf')])
        self.assertTrue(os.path.exists(result_path))

    def test_compress_single_file_with_output_path(self):
        result_path = './TestData/new-min.pdf'
        self.remove_if_not_exists(result_path)
        OsUtility.clean_up_folder(os.path.abspath("./TestData/multiPageTestData_tmp"))

        subprocess.call(["python3", os.path.abspath('../pdfcompressor.py'),
                         "-p", os.path.abspath('./TestData/multiPageTestData.pdf'),
                         "-o", os.path.abspath(result_path), "-m", "9"])
        file_exists = os.path.exists(result_path)
        os.remove(result_path)
        self.assertTrue(file_exists)

    # TODO relative paths
