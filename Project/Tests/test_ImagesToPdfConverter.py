import os.path
import shutil
import sys
from io import StringIO
from unittest import TestCase

from Project.Converter.ImagesToPdfConverter import ImagesToPdfConverter
from Project.Converter.PdfToImageConverter import PdfToImageConverter
from Project.Utility.OsUtility import OsUtility


class TestPdfToImagesConverter(TestCase):
    working_dir: str = os.path.abspath(r"./CurrentWorkingPathTest/")
    dest_file: str = os.path.abspath(r"./TestData/result.pdf")

    def test_class_init_simple(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf")

    def test_class_init_with_pytesseract_path(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", r"pathToPyTesseract")

    def test_class_init_without_force_ocr(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", r"pathToPyTesseract", False)

    def test_class_init_with_force_ocr(self):
        test_stout = StringIO()
        sys.stdout = test_stout
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", r"pathToPyTesseract", True)
        self.assertEqual(test_stout.getvalue(), "")  # TODO maybe change condition

    def test_single_page_pdf_without_ocr(self):
        if os.path.exists(self.dest_file):
            os.remove(self.dest_file)
        pdf_converter = PdfToImageConverter(r"./TestData/singlePagePdf.pdf",
                                            self.working_dir, 1)
        pdf_converter.convert()
        image_converter = ImagesToPdfConverter(self.working_dir, self.dest_file)
        image_converter.convert()
        self.assertTrue(os.path.exists(self.dest_file))
        OsUtility.clean_up_folder(self.working_dir)

    def test_single_page_pdf_wit_ocr(self):
        self.fail("not implemented yet")