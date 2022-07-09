import os.path
import shutil
from unittest import TestCase

from Project.Converter.PdfToImageConverter import PdfToImageConverter
from Project.Utility.OsUtility import OsUtility


class TestPdfToImagesConverter(TestCase):
    working_dir = os.path.abspath(r"./CurrentWorkingPathTest/")

    def test_class_init(self):
        # without mode
        PdfToImageConverter("originFile.pdf", "destinationFile.pdf")
        # with mode
        PdfToImageConverter("originFile.pdf", "destinationFile.pdf", 5)

    def test_single_page_pdf_convert(self):
        pdf_converter = PdfToImageConverter(r"./TestData/singlePagePdf.pdf",
                                            self.working_dir, 5)
        pdf_converter.convert()
        self.assertTrue(os.path.exists(self.working_dir+"/page_0.png"))
        self.assertFalse(os.path.exists(self.working_dir + "/page_1.png"))

    def test_multiple_page_pdf_convert(self):
        pdf_converter = PdfToImageConverter(r"./TestData/multiPageTestData.pdf",
                                            self.working_dir, 1)
        pdf_converter.convert()
        self.assertTrue(os.path.exists(self.working_dir + "/page_0.png"))
        self.assertTrue(os.path.exists(self.working_dir + "/page_1.png"))
        self.assertFalse(os.path.exists(self.working_dir + "/page_2.png"))

    def test_wrong_format_pdf(self):
        # TODO expected exception
        pdf_converter = PdfToImageConverter(r"./TestData/multiPageTestData.pdf",
                                            self.working_dir, 1)
        pdf_converter.convert()
        self.assertTrue(os.path.exists(self.working_dir + "/page_0.png"))
        self.assertTrue(os.path.exists(self.working_dir + "/page_1.png"))
        self.assertFalse(os.path.exists(self.working_dir + "/page_2.png"))

    def test_mode_is_min_value(self):
        pdf_converter = PdfToImageConverter(r"./TestData/multiPageTestData.pdf",
                                            self.working_dir, 0)
        self.assertRaises(RuntimeError, pdf_converter.convert)

    def test_mode_is_max_value(self):
        pdf_converter = PdfToImageConverter(r"./TestData/multiPageTestData.pdf",
                                            self.working_dir, 10)
        pdf_converter.convert()
        self.assertTrue(os.path.exists(self.working_dir + "/page_0.png"))
        self.assertTrue(os.path.exists(self.working_dir + "/page_1.png"))
        self.assertFalse(os.path.exists(self.working_dir + "/page_2.png"))

    def test_mode_is_negative_value(self):

        pdf_converter = PdfToImageConverter(r"./TestData/multiPageTestData.pdf",
                                            self.working_dir, -1)
        pdf_converter.convert()
        self.assertTrue(os.path.exists(self.working_dir + "/page_0.png"))
        self.assertTrue(os.path.exists(self.working_dir + "/page_1.png"))
        self.assertFalse(os.path.exists(self.working_dir + "/page_2.png"))

    def test_mode_is_too_large_value(self):
        pdf_converter = PdfToImageConverter(r"./TestData/multiPageTestData.pdf",
                                            self.working_dir, 11)
        pdf_converter.convert()
        self.assertTrue(os.path.exists(self.working_dir + "/page_0.png"))
        self.assertTrue(os.path.exists(self.working_dir + "/page_1.png"))
        self.assertFalse(os.path.exists(self.working_dir + "/page_2.png"))

    def setUp(self):
        OsUtility.clean_up_folder(self.working_dir)

    def tearDown(self):
        if os.path.isdir(self.working_dir):
            shutil.rmtree(self.working_dir)

# TODO different filename tests
