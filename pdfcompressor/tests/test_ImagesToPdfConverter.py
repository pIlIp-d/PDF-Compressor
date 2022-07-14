import os.path
from unittest import TestCase


class TestPdfToImagesConverter(TestCase):
    working_dir: str = os.path.abspath(r"./CurrentWorkingPathTest/")
    dest_file: str = os.path.abspath(r"TestData/TestFolder/result.pdf")
    tesseract_path: str = r"/usr/bin/tesseract"
