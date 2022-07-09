import os.path
from unittest import TestCase

from Project.Converter.PdfToImageConverter import PdfToImageConverter


class TestPdfToImagesConverter(TestCase):

    def test_class_init(self):
        # without mode
        PdfToImageConverter("originFile.pdf", "destinationFile.pdf")
        # with mode
        PdfToImageConverter("originFile.pdf", "destinationFile.pdf", 5)

    def test_single_page_pdf_convert(self):
        self.fail("Not Implemented Yet")

    def test_multiple_page_pdf_convert(self):
        self.fail("Not Implemented Yet")

    def test_wrong_format_pdf(self):
        self.fail("Not Implemented Yet")

    def test_mode_is_0(self):
        self.fail("Not Implemented Yet")

    def test_mode_is_10(self):
        self.fail("Not Implemented Yet")

    def test_mode_is_5(self):
        self.fail("Not Implemented Yet")

# TODO different filename tests
