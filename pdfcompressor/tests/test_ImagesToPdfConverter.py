import os.path
import sys
from io import StringIO
from unittest import TestCase

from pdfcompressor.compressor.converter.ImagesToPdfConverter import ImagesToPdfConverter
from pdfcompressor.compressor.converter.PdfToImageConverter import PdfToImageConverter
from pdfcompressor.utility.ConsoleUtility import ConsoleUtility
from pdfcompressor.utility.OsUtility import OsUtility


class TestPdfToImagesConverter(TestCase):
    working_dir: str = os.path.abspath(r"./CurrentWorkingPathTest/")
    dest_file: str = os.path.abspath(r"TestData/TestFolder/result.pdf")
    tesseract_path: str = r"/usr/bin/tesseract"
    # r"/home/user/Downloads/tesseract-ocr-w64-setup-v5.2.0.20220708.exe"

    def test_class_init_simple(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf")

    def test_class_init_with_pytesseract_path(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", self.tesseract_path)

    def test_class_init_without_force_ocr(self):
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", self.tesseract_path, False)

    def test_class_init_with_force_ocr(self):
        test_stout = StringIO()
        sys.stdout = test_stout
        ImagesToPdfConverter("originFile.pdf", "destinationFile.pdf", self.tesseract_path, True)

        # check that  no error occurred
        self.assertFalse(test_stout.getvalue().__contains__(ConsoleUtility.RED))

    def test_single_page_pdf_without_ocr(self):
        if os.path.exists(self.dest_file):
            os.remove(self.dest_file)
        pdf_converter = PdfToImageConverter(r"TestData/TestFolder/singlePagePdf.pdf",
                                            self.working_dir, 1)
        pdf_converter.convert()
        image_converter = ImagesToPdfConverter(self.working_dir, self.dest_file, self.tesseract_path, False)
        image_converter.convert()
        self.assertTrue(os.path.exists(self.dest_file))
        OsUtility.clean_up_folder(self.working_dir)

    def test_single_page_pdf_wit_ocr(self):
        test_stout = StringIO()
        sys.stdout = test_stout

        if os.path.exists(self.dest_file):
            os.remove(self.dest_file)
        pdf_converter = PdfToImageConverter(r"TestData/TestFolder/singlePagePdf.pdf",
                                            self.working_dir, 1)
        pdf_converter.convert()
        image_converter = ImagesToPdfConverter(self.working_dir, self.dest_file, self.tesseract_path, True)
        image_converter.convert()
        self.assertTrue(os.path.exists(self.dest_file))
        OsUtility.clean_up_folder(self.working_dir)
        # check that  no error occurred
        self.assertFalse(test_stout.getvalue().__contains__(ConsoleUtility.RED))
