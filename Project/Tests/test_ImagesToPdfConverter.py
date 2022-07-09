import os.path
import shutil
import sys
from io import StringIO
from unittest import TestCase

from Project.Converter.ImagesToPdfConverter import ImagesToPdfConverter
from Project.Converter.PdfToImageConverter import PdfToImageConverter
from Project.Utility.OsUtility import OsUtility


class TestPdfToImagesConverter(TestCase):
    working_dir = os.path.abspath(r"./CurrentWorkingPathTest/")

    def test_class_init_simple(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf")

    def test_class_init_with_mode(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", 5)

    def test_class_init_with_mode_and_pytesseract_path(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", 5, r"pathToPyTesseract")

    def test_class_init_without_force_ocr(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", 5, r"pathToPyTesseract", False)

    def test_class_init_with_force_ocr(self):
        testStout = StringIO()
        sys.stdout = testStout
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", 5, r"pathToPyTesseract", True)
        self.assertEqual(testStout.getvalue(), "")  # TODO maybe change condition
