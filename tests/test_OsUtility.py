import os.path
import shutil
from unittest import TestCase

import jsons

from django_app.utility.os_utility import OsUtility
from plugins.crunch_compressor.config import get_config


class TestOsUtility(TestCase):
    CONFIG_FILE: str = os.path.abspath(os.path.join("../plugins/crunch_compressor", "..", "config.json"))

    @staticmethod
    def create_file(file_path: str) -> None:
        with open(file_path, "w") as f:
            f.write("")

    @staticmethod
    def create_folder(folder_path: str) -> None:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)

    # get_file_list
    def test_get_file_list_with_empty_folder_as_path(self):
        folder = "./TestData/newEmptyFolder"
        self.create_folder(folder)
        file_list = OsUtility.get_file_list(folder)
        shutil.rmtree(folder)
        self.assertEqual([], file_list)

    def test_get_file_list_with_single_file_as_path(self):
        self.assertEqual(1, len(OsUtility.get_file_list("./TestData/testFile.txt")))

    def test_get_file_list_with_single_file_in_folder_as_path(self):
        self.assertEqual(1, len(OsUtility.get_file_list("./TestData/testFolderWithOneFile")))

    def test_get_file_list_with_multiple_files_in_folder_as_path(self):
        self.assertEqual(2, len(OsUtility.get_file_list("./TestData/testFolder", ".txt")))

    def test_get_file_list_with_no_path_indication_at_start_as_path(self):
        self.assertEqual(1, len(OsUtility.get_file_list("TestData/testFile.txt")))

    def test_get_file_list_path_doesnt_exist_as_path(self):
        self.assertEqual(0, len(OsUtility.get_file_list("TestData/noFolder")))

    def test_get_file_list_with_empty_string_as_path(self):
        self.assertEqual(0, len(OsUtility.get_file_list("", ".txt")))

    def test_get_file_list_from_absolute_path(self):
        self.assertEqual(1, len(OsUtility.get_file_list(os.path.abspath("./TestData/testFile.txt"), ".txt")))

    def test_get_file_list_with_default_ending(self):
        self.assertEqual(3, len(OsUtility.get_file_list("./TestData/testFolder")))

    def test_get_file_list_with_empty_ending(self):
        self.assertEqual(3, len(OsUtility.get_file_list("./TestData/testFolder", "")))

    def test_get_file_list_with_custom_ending(self):
        self.assertEqual(2, len(OsUtility.get_file_list("./TestData/testFolder", ".txt")))
        self.assertEqual(1, len(OsUtility.get_file_list("./TestData/testFolder", ".md")))

    def test_get_file_list_with_only_dot_as_ending(self):
        self.assertEqual(0, len(OsUtility.get_file_list("./TestData/testFolder", ".")))
        if os.name == "nt":
            self.fail("dots as file ending are not supported on windows.")
        folder = "./TestData/createdFolder"
        self.create_folder(folder)
        file = os.path.join(folder, "file_with_dot.")
        self.create_file(file)
        file_list = OsUtility.get_file_list(folder, ".")
        shutil.rmtree(folder)
        self.assertEqual(1, len(file_list))

    def test_get_file_list_with_some_text_as_ending(self):
        self.assertEqual(0, len(OsUtility.get_file_list("./TestData/testFolder", "endsWithSomeText")))
        folder = "./TestData/createdFolder"
        self.create_folder(folder)
        file1 = os.path.join(folder, "file_endsWithSomeText")
        file2 = os.path.join(folder, "some_other_file")
        self.create_file(file1)
        self.create_file(file2)
        file_list = OsUtility.get_file_list(folder, "endsWithSomeText")
        shutil.rmtree(folder)
        self.assertEqual(1, len(file_list))

    def test_get_file_list_with_no_file_found_by_ending(self):
        self.assertEqual(0, len(OsUtility.get_file_list("./TestData/testFolder", ".svg")))

    # clean_up_folder
    def test_clean_up_folder_with_empty_folder(self):
        folder_dir = os.path.join(".", "TestData", "newEmptyFolder")
        self.create_folder(folder_dir)

        OsUtility.clean_up_folder(folder_dir)

        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_files_in_folder(self):
        folder_dir = os.path.join(".", "TestData", "filledCreatedFolder")
        self.create_folder(folder_dir)

        self.create_file(os.path.join(folder_dir, "testFile1.png"))
        self.create_file(os.path.join(folder_dir, "testFile2.png"))

        OsUtility.clean_up_folder(folder_dir)

        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_not_existing_folder(self):
        OsUtility.clean_up_folder("./TestData/noFolder")

    def test_clean_up_folder_with_relative_path_to_existing_file(self):
        file = os.path.join(".", "TestData", "createdFile.txt")
        self.create_file(file)
        self.assertRaises(
            ValueError,
            OsUtility.clean_up_folder, file
        )
        os.remove(file)

    def test_clean_up_folder_with_relative_path_to_existing_folder(self):
        folder_dir = os.path.join(".", "TestData", "createdFolder")
        self.create_folder(folder_dir)

        OsUtility.clean_up_folder(folder_dir)
        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_absolute_path_to_existing_file(self):
        file = os.path.join(".", "TestData", "createdFile.txt")
        self.create_file(file)
        self.assertRaises(
            ValueError,
            OsUtility.clean_up_folder, os.path.abspath(file)
        )
        os.remove(file)

    def test_clean_up_folder_with_absolute_path_to_existing_folder(self):
        folder_dir = os.path.join(".", "TestData", "createdFolder")
        self.create_folder(folder_dir)

        OsUtility.clean_up_folder(folder_dir)
        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_empty_path_string(self):
        OsUtility.clean_up_folder("")

    # get_filename
    def test_get_filename_with_file_without_file_ending(self):
        file = os.path.join("./TestData/fileWithoutFileEnding")
        self.assertEqual("fileWithoutFileEnding", OsUtility.get_filename(file))

    def test_get_filename_with_relative_path_to_file(self):
        file = os.path.join("./singlePagePdf.pdf")
        self.assertEqual("singlePagePdf", OsUtility.get_filename(file))

    def test_get_filename_with_absolute_path_to_file(self):
        file = os.path.join(os.path.abspath("../plugins/crunch_compressor/tests/TestData/singlePagePdf.pdf"))
        self.assertEqual("singlePagePdf", OsUtility.get_filename(file))

    def test_get_filename_with_relative_path_to_folder(self):
        file = os.path.join("../plugins/crunch_compressor/tests/TestData/TestFolder")
        self.assertEqual("TestFolder", OsUtility.get_filename(file))

    def test_get_filename_with_absolute_path_to_folder(self):
        file = os.path.join(os.path.abspath(os.path.join("", "../plugins/crunch_compressor/tests/TestData", "TestFolder")))
        self.assertEqual("TestFolder", OsUtility.get_filename(file))

    def test_get_filename_with_invalid_path(self):
        file = os.path.join(os.path.abspath("../plugins/crunch_compressor/tests/TestData/singlePagePdf.pdf"))
        self.assertEqual("singlePagePdf", OsUtility.get_filename(file))

        file2 = os.path.join(os.path.abspath("SomeRubbishTest-LALA-File_folder(jjkn)"))
        self.assertEqual("SomeRubbishTest-LALA-File_folder(jjkn)", OsUtility.get_filename(file2))

    def test_get_filename_with_empty_string_as_path(self):
        self.assertEqual("", OsUtility.get_filename(""))

    def test_get_filename_with_dot_at_end_of_string_as_path(self):
        self.assertEqual("filename", OsUtility.get_filename("filename."))

    def test_get_filename_with_custom_file_ending_path(self):
        self.assertEqual("filename", OsUtility.get_filename("filename.old.pdf", r"\..+\..+"))

    def test_os_utility_get_config_file_not_found(self):
        shutil.move(self.CONFIG_FILE, self.CONFIG_FILE + ".tmp")
        self.assertRaises(
            FileNotFoundError,
            get_config,
            self.CONFIG_FILE
        )
        # move tmp file back
        shutil.move(self.CONFIG_FILE + ".tmp", self.CONFIG_FILE)

    def test_os_utility_get_config_all_values_set(self):
        # no error -> all must have been set
        get_config(self.CONFIG_FILE)

    def test_os_utility_get_config_not_all_values_are_set(self):
        shutil.copyfile(self.CONFIG_FILE, self.CONFIG_FILE + ".tmp")

        with open(self.CONFIG_FILE, "r") as config_file:
            json = jsons.loads(config_file.read())

        with open(self.CONFIG_FILE, "w") as config_file:
            json.pop("cpdfsqueeze_path", None)
            config_file.write(jsons.dumps(json))
        self.assertRaises(
            TypeError,
            get_config,
            self.CONFIG_FILE
        )
        shutil.move(self.CONFIG_FILE + ".tmp", self.CONFIG_FILE)

    def test_os_utility_get_file_size_file_doesnt_exist(self):
        self.assertEqual(0, OsUtility.get_file_size(os.path.join("", "file_not_exists.pdf")))

    def test_os_utility_get_file_size_relative_path(self):
        self.assertNotEqual(0, OsUtility.get_file_size(os.path.join("", "../plugins/crunch_compressor/tests/TestData", "singlePagePdf.pdf")))

    def test_os_utility_get_file_size_absolute_path(self):
        self.assertNotEqual(0, OsUtility.get_file_size(
            os.path.abspath(os.path.join("", "../plugins/crunch_compressor/tests/TestData", "singlePagePdf.pdf")))
        )

    def test_os_utility_get_file_size_compare_results(self):
        self.assertTrue(
            OsUtility.get_file_size(os.path.join("", "../plugins/crunch_compressor/tests/TestData", "singlePagePdf.pdf"))
            <
            OsUtility.get_file_size(os.path.join("", "../plugins/crunch_compressor/tests/TestData", "multiPageTestData.pdf"))
        )

    def test_os_utility_get_file_size_on_filled_folder(self):
        self.assertEqual(0, OsUtility.get_file_size(os.path.join("", "../plugins/crunch_compressor/tests/TestData")))

    def test_os_utility_get_file_size_on_empty_folder(self):
        empty_dir = os.path.join("", "../plugins/crunch_compressor/tests/TestData", "emptyFolder")
        if not os.path.isdir(empty_dir):
            os.mkdir(empty_dir)
        self.assertEqual(0, OsUtility.get_file_size(empty_dir))
        os.removedirs(empty_dir)

    def test_os_utility_get_file_size_on_not_existing_folder(self):
        empty_dir = os.path.join("", "../plugins/crunch_compressor/tests/TestData", "not_existing_folder")
        if os.path.isdir(empty_dir):
            os.removedirs(empty_dir)
        self.assertEqual(0, OsUtility.get_file_size(empty_dir))

    def test_get_path_without_file_ending(self):
        file_without = os.path.join("../plugins/crunch_compressor/tests", "directory", "file")
        file_with = file_without + ".txt"
        self.assertEqual(file_without, OsUtility.get_path_without_file_ending(file_with))

    @classmethod
    def tearDownClass(cls) -> None:
        # reset if get_config() test has failed
        if os.path.exists(cls.CONFIG_FILE + ".tmp"):
            shutil.move(cls.CONFIG_FILE + ".tmp", cls.CONFIG_FILE)
