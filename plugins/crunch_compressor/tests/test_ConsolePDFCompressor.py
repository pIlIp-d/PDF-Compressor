import os.path
import shutil
import subprocess
import sys
import time
from io import StringIO
from unittest import TestCase

from plugins.crunch_compressor.utility.console_utility import ConsoleUtility
from plugins.crunch_compressor.utility.os_utility import OsUtility


class TestConsolePDFCompressor(TestCase):
    program_path: str = os.path.abspath('../../..')

    @staticmethod
    def remove_if_not_exists(file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.exists(file_path):
            shutil.rmtree(file_path)

    @staticmethod
    def get_console_buffer() -> StringIO:
        console_buffer = StringIO()
        sys.stdout = console_buffer
        return console_buffer

    # TODO testUtility to avoid duplicates
    @staticmethod
    def create_folder(folder_path: str) -> None:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)

    @staticmethod
    def create_file(file_path: str) -> None:
        with open(file_path, "w") as f:
            f.write("")

    # input path
    def test_pdf_compressor_valid_path(self):
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf")
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    def test_pdf_compressor_more_than_one_page(self):
        result_path = os.path.join("", "TestData", "TestFolder", "multiPageTestData_compressed.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "TestFolder", "multiPageTestData.pdf")
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compressor_valid_path_with_space(self):
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("", "TestData", "single Page Pdf_compressed.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "single Page Pdf.pdf")
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    def test_pdf_compressor_valid_path_with_space_but_without_quotes(self):
        # TODO supress console output
        console_buffer = self.get_console_buffer()
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "") + "single", "Page", "Pdf.pdf"
        ])
        self.assertFalse(console_buffer.getvalue().__contains__("ValueError"))
        self.assertEqual(2, return_code)

    def test_pdf_compressor_invalid_path_not_exist(self):
        # TODO supress console output
        console_buffer = self.get_console_buffer()
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "notExistingFile.pdf")
        ])
        self.assertFalse(console_buffer.getvalue().__contains__("ValueError"))
        self.assertEqual(1, return_code)

    def test_pdf_compressor_valid_folder_with_slash_at_the_end_as_path(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed"))
        # TODO supress console output
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "") + "TestFolder/"
        ])
        output_files = OsUtility.get_file_list(result_path)
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "singlePagePdf.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "multiPageTestData.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "result.pdf"))))
        shutil.rmtree(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compressor_empty_folder_as_path(self):
        folder = os.path.join(os.path.realpath(""), "TestData", "EmptyFolder")
        self.create_folder(folder)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", folder
        ])
        self.assertEqual(0, return_code)
        shutil.rmtree(folder)

    def test_pdf_compressor_invalid_folder_as_path(self):
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "notExistingFolder")
        ])
        self.assertEqual(1, return_code)

    def test_pdf_compressor_valid_relative_file_path(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "singlePagePdf_compressed.pdf"))
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", './TestData/singlePagePdf.pdf'
        ])
        self.assertTrue(os.path.isfile(result_path))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compressor_valid_absolute_file_path(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "singlePagePdf_compressed.pdf"))
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.abspath('TestData/singlePagePdf.pdf')
        ])
        self.assertTrue(os.path.isfile(result_path))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compressor_valid_relative_folder_path(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed"))
        # TODO supress console output
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join("", "TestData", "TestFolder")
        ])
        output_files = OsUtility.get_file_list(result_path)
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "singlePagePdf.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "multiPageTestData.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "result.pdf"))))
        shutil.rmtree(result_path)

        self.assertEqual(0, return_code)

    def test_pdf_compressor_valid_absolute_folder_path(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed"))
        # TODO supress console output
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.abspath(os.path.join("", "TestData", "TestFolder"))
        ])
        output_files = OsUtility.get_file_list(result_path)
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "singlePagePdf.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "multiPageTestData.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "result.pdf"))))
        shutil.rmtree(result_path)

        self.assertEqual(0, return_code)

    def test_pdf_compressor_path_doesnt_start_with_dot_or_slash(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed"))
        # TODO supress console output
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join("TestData", "TestFolder")
        ])
        output_files = OsUtility.get_file_list(result_path)
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "singlePagePdf.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "multiPageTestData.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "TestFolder_compressed", "result.pdf"))))
        shutil.rmtree(result_path)

        self.assertEqual(0, return_code)

    # mode
    def defaultTestForMode(self, mode: int):
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf"),
            "--mode", str(mode)
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    def test_pdf_compressor_with_minimum_mode(self):
        self.defaultTestForMode(1)

    def test_pdf_compressor_with_maximum_mode(self):
        self.defaultTestForMode(5)

    def test_pdf_compressor_too_low_mode(self):
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf"),
            "--mode", "0"
        ])
        self.assertEqual(1, return_code)

    def test_pdf_compressor_too_big_mode(self):
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf"),
            "--mode", "6"
        ])
        self.assertEqual(1, return_code)

    def test_pdf_compressor_compare_smallest_and_biggest_mode(self):
        # todo time measurement
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        input_file = os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf")
        self.remove_if_not_exists(result_path)
        time1 = time.time()
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_file,
            "--mode", "1"
        ])
        time1 = time.time() - time1
        first_file_size = os.stat(result_path).st_size

        time2 = time.time()
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_file,
            "--mode", "5"
        ])
        time2 = time.time() - time2
        second_file_size = os.stat(result_path).st_size
        os.remove(result_path)
        self.assertTrue(first_file_size <= second_file_size and time1 >= time2)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    def test_pdf_compressor_output_file_already_exists(self):
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("", "TestData", "result.pdf")
        self.remove_if_not_exists(result_path)
        self.create_file(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf"),
            "-o", result_path
        ])
        self.assertTrue(os.path.isfile(result_path))
        os.remove(result_path)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    def test_pdf_compressor_file_as_input_and_directory_as_output(self):
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("", "TestData", "NewTestFolder")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf"),
            "-o", result_path
        ])
        self.assertTrue(os.path.exists(result_path))
        shutil.rmtree(result_path)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    def test_pdf_compressor_directory_as_input_and_directory_as_output(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "NewTestFolder"))
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.abspath(os.path.join("", "TestData", "TestFolder")),
            "-o", result_path
        ])
        self.assertTrue(os.path.exists(result_path))
        output_files = OsUtility.get_file_list(result_path)
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "NewTestFolder", "singlePagePdf.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "NewTestFolder", "multiPageTestData.pdf"))))
        self.assertTrue(output_files.__contains__(
            os.path.abspath(os.path.join("", "TestData", "NewTestFolder", "result.pdf"))))
        shutil.rmtree(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compressor_directory_as_input_and_file_as_output(self):
        result_path = os.path.join("", "TestData", "result.pdf")
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.abspath(os.path.join("", "TestData", "TestFolder")),
            "-o", result_path
        ])
        self.assertTrue(os.path.exists(result_path))
        self.remove_if_not_exists(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compressor_invalid_output_path_start_char(self):
        console_buffer = self.get_console_buffer()
        result_path = os.path.join("TestData", "result.pdf")
        self.remove_if_not_exists(result_path)
        self.create_file(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf"),
            "-o", result_path
        ])
        self.assertTrue(os.path.isfile(result_path))
        os.remove(result_path)
        self.assertFalse(console_buffer.getvalue().__contains__(ConsoleUtility.RED))
        self.assertEqual(0, return_code)

    # --force-ocr
    def test_pdf_compress_force_ocr_active_and_compression_succeeded(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "result.pdf"))
        input_file = os.path.abspath(os.path.join("", "TestData", "singlePagePdf.pdf"))
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_file,
            "-o", result_path,
            "--force-ocr",
            "--dpi", "200"
        ])
        self.assertTrue(os.path.exists(result_path))
        self.assertTrue(OsUtility.get_file_size(result_path) < OsUtility.get_file_size(input_file))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compress_force_ocr_active_and_compression_not_succeeded(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "result.pdf"))
        input_file = os.path.abspath(os.path.join("", "TestData", "pdfMaxCompressedForMode3.pdf"))
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_file,
            "-o", result_path,
            "--force-ocr"
        ])
        self.assertTrue(os.path.exists(result_path))
        self.assertFalse(OsUtility.get_file_size(result_path) < OsUtility.get_file_size(input_file))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compress_force_ocr_active_and_no_ocr(self):
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", os.path.abspath(os.path.join("", "TestData", "singlePagePdf.pdf")),
            "--force-ocr",
            "--no-ocr"
        ])
        self.assertEqual(1, return_code)

    def test_pdf_compress_no_force_ocr_active_and_compression_succeeded(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "result.pdf"))
        input_file = os.path.abspath(os.path.join("", "TestData", "singlePagePdf.pdf"))
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-o", result_path,
            "-p", input_file
        ])
        self.assertTrue(os.path.exists(result_path))
        self.assertTrue(OsUtility.get_file_size(result_path) < OsUtility.get_file_size(input_file))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compress_no_force_ocr_active_and_compression_not_succeeded(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "pdfMaxCompressedOutput.pdf"))
        input_file = os.path.abspath(os.path.join("", "TestData", "pdfMaxCompressedForMode3.pdf"))
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-o", result_path,
            "-p", input_file,
            "-m", "3"
        ])
        self.assertTrue(os.path.exists(result_path))
        self.assertEqual(OsUtility.get_file_size(result_path), OsUtility.get_file_size(input_file))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compress_no_force_ocr_active_and_no_ocr(self):
        result_path = os.path.abspath(os.path.join("", "TestData", "pdfMaxCompressedOutput.pdf"))
        input_file = os.path.abspath(os.path.join("", "TestData", "pdfMaxCompressedForMode3.pdf"))
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_file,
            "-o", result_path,
            "--no-ocr"
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compress_simple_and_lossless(self):
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        input_path = os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_path,
            "--simple-and-lossless"
        ])
        first_file_size = os.stat(input_path).st_size
        second_file_size = os.stat(result_path).st_size
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertTrue(first_file_size > second_file_size)
        self.assertEqual(0, return_code)

    def test_pdf_compress_no_special_dpi(self):
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        input_path = os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_path,
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    def test_pdf_compress_dpi_small_smaller_than_big(self):
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        input_path = os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf")
        self.remove_if_not_exists(result_path)
        return_code1 = subprocess.call([
            "python3", self.program_path,
            "-p", input_path,
            "--dpi", "100"
        ])
        first_file_size = os.stat(result_path).st_size
        return_code2 = subprocess.call([
            "python3", self.program_path,
            "-p", input_path,
            "--dpi", "500"
        ])
        second_file_size = os.stat(result_path).st_size
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertTrue(first_file_size < second_file_size)
        self.assertEqual(0, return_code1)
        self.assertEqual(0, return_code2)

    def test_pdf_compress_with_dpi_and_simple_and_lossless(self):
        result_path = os.path.join("", "TestData", "singlePagePdf_compressed.pdf")
        input_path = os.path.join(os.path.realpath(""), "TestData", "singlePagePdf.pdf")
        self.remove_if_not_exists(result_path)
        return_code = subprocess.call([
            "python3", self.program_path,
            "-p", input_path,
            "--dpi", "100",
            "--simple-and-lossless"
        ])
        self.assertTrue(os.path.exists(result_path))
        os.remove(result_path)
        self.assertEqual(0, return_code)

    @classmethod
    def tearDownClass(cls) -> None:
        # remove all ..._temp folders in project root that are left over because of failure
        project_root = os.path.join("..", "..")
        for r, d, _ in os.walk(project_root):
            for folder_name in d:
                if not folder_name.endswith("_tmp"):
                    continue

                shutil.rmtree(os.path.join(r, folder_name))
            break
