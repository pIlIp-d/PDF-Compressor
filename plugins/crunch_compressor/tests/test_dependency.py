import os
from unittest import TestCase
import jsons

from plugins.crunch_compressor.compressor.pdf_compressor.pdf_crunch_compressor import PDFCrunchCompressor
from django_app.utility.os_utility import OsUtility
from tests.help_classes import get_console_buffer


class TestDependency(TestCase):
    config_file = os.path.join(os.path.dirname(__file__), "..", "config.json")
    temp_config_file = config_file + ".tmp"

    test_data_dir = os.path.join(os.path.dirname(__file__), "TestData")
    source_path = os.path.join(test_data_dir, "singlePagePdf.pdf")
    result_path = os.path.join(test_data_dir, "singlePagePdf_processed.pdf")

    @staticmethod
    def _run_pdf_compressor(**kwargs):
        if "default_pdf_dpi" not in kwargs:
            kwargs["default_pdf_dpi"] = 20
        source_path = kwargs.pop("source_path")
        PDFCrunchCompressor(**kwargs).process(source_path)

    def __run_simple_compression(self, assume_success: bool, simple_and_lossless: bool) -> None:
        if os.path.isfile(self.result_path):
            os.remove(self.result_path)

        args = {"source_path": self.source_path}
        if simple_and_lossless:
            args["simple_and_lossless"] = True
        std_err_buffer = get_console_buffer("stderr")
        self._run_pdf_compressor(**args)

        # return_code, output_str, err_str =
        if assume_success or simple_and_lossless:
            path_exists = os.path.exists(self.result_path)
            if path_exists:
                os.remove(self.result_path)
            self.assertTrue(path_exists)
            # self.assertEqual(0, return_code)
        else:
            self.assertNotEqual("", std_err_buffer)

    def __get_config(self):
        with open(self.config_file, "r") as f:
            return jsons.loads(f.read())

    def __write_new_config(self, json_config: object):
        with open(self.config_file, "w") as f:
            f.write(jsons.dumps(json_config))

    def __change_path(self, path_to_change: str, new_path_value: str):
        config = self.__get_config()
        config[path_to_change] = new_path_value
        self.__write_new_config(config)

    def __change_to_empty_path(self, path_to_change: str):
        self.__change_path(path_to_change, "")

    def __change_to_invalid_path(self, path_to_change: str):
        self.__change_path(path_to_change, "some_invalid/path")

    def test_with_advpng_path_is_empty(self):
        self.__change_to_empty_path("advpng_path")
        self.__run_simple_compression(False, False)

    def test_with_advpng_path_is_valid(self):
        self.__run_simple_compression(True, False)

    def test_with_advpng_path_is_invalid(self):
        self.__change_to_invalid_path("advpng_path")
        self.__run_simple_compression(False, False)

    def test_with_advpng_path_is_valid_with_simple_and_lossless(self):  # should be valid for all paths
        self.__run_simple_compression(True, True)

    def test_with_advpng_path_is_invalid_with_simple_and_lossless(self):
        self.__change_to_invalid_path("advpng_path")
        self.__run_simple_compression(True, True)

    def test_with_pngquant_path_is_empty(self):
        self.__change_to_empty_path("pngquant_path")
        self.__run_simple_compression(False, False)

    def test_with_pngquant_path_is_invalid(self):
        self.__change_to_invalid_path("pngquant_path")
        self.__run_simple_compression(False, False)

    def test_with_pngquant_path_is_invalid_with_simple_and_lossless(self):
        self.__change_to_invalid_path("pngquant_path")
        self.__run_simple_compression(True, True)

    def test_with_pngcrush_path_is_empty(self):
        self.__change_to_empty_path("pngcrush_path")
        self.__run_simple_compression(False, False)

    def test_with_pngcrush_path_is_invalid(self):
        self.__change_to_invalid_path("pngcrush_path")
        self.__run_simple_compression(False, False)

    def test_with_pngcrush_path_is_invalid_with_simple_and_lossless(self):
        self.__change_to_invalid_path("pngcrush_path")
        self.__run_simple_compression(True, True)

    def test_with_cpdfsqueeze_path_is_empty(self):
        self.__change_to_empty_path("cpdfsqueeze_path")
        self.__run_simple_compression(False, False)

    def test_with_cpdfsqueeze_path_is_invalid(self):  # TODO test cpdf_path with wine add on and the fails without wine
        self.__change_to_invalid_path("cpdfsqueeze_path")
        self.__run_simple_compression(False, False)

    def test_with_cpdfsqueeze_path_is_invalid_with_simple_and_lossless(self):
        self.__change_to_invalid_path("cpdfsqueeze_path")

        if os.path.isfile(self.result_path):
            os.remove(self.result_path)

        args = {
            "source_path": self.source_path,
            "simple_and_lossless": True
        }
        self.assertRaises(ValueError, self._run_pdf_compressor, **args)
        self.assertFalse(os.path.exists(self.result_path))

    def test_with_tesseract_path_is_empty(self):
        self.__change_to_empty_path("tesseract_path")
        self.__run_simple_compression(False, False)

    def test_with_tesseract_path_is_invalid(self):
        self.__change_to_invalid_path("tesseract_path")
        self.__run_simple_compression(False, False)

    # TODO precondition
    def test_with_tessdata_prefix_is_empty(self):
        self.fail("Not implemented yet")

    def test_with_tessdata_prefix_is_valid(self):
        self.fail("Not implemented yet")

    def test_with_tessdata_prefix_is_invalid(self):
        self.fail("Not implemented yet")

    def test_tesseract_with_no_ocr(self):
        self.fail("Not implemented yet")

    def setUp(self) -> None:
        # save the original config file as a copy
        OsUtility.copy_file(self.config_file, self.temp_config_file)

    def tearDown(self) -> None:
        # restore the original config file
        OsUtility.move_file(os.path.abspath(self.temp_config_file), os.path.abspath(self.config_file))
        if os.path.isfile(self.result_path):
            os.remove(self.result_path)
