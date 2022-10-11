import os.path
import shutil
from unittest import TestCase

import jsons

from plugins.crunch_compressor.utility.os_utility import OsUtility


class TestOsUtility(TestCase):
    CONFIG_FILE: str = os.path.abspath(os.path.join("..", "..", "config.json"))

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
    def test_get_file_list_from_empty_folder(self):
        folder_dir = os.path.join("", "TestData", "emptyFolder")
        self.create_folder(folder_dir)
        file_list = OsUtility.get_file_list(folder_dir)
        shutil.rmtree(folder_dir)
        self.assertEqual(0, len(file_list))

    def test_get_file_list_from_single_file_in_folder(self):
        folder_dir = os.path.join("", "TestData", "singleFileFolder")
        self.create_folder(folder_dir)

        file = os.path.join(folder_dir, "testFile.png")
        self.create_file(file)

        file_list = OsUtility.get_file_list(folder_dir)
        shutil.rmtree(folder_dir)

        self.assertEqual(1, len(file_list))
        self.assertEqual(file, file_list[0])

    def test_get_file_list_from_multiple_files_in_folder(self):
        folder_dir = os.path.join("", "TestData", "singleFileFolder")
        self.create_folder(folder_dir)

        file1 = os.path.join(folder_dir, "testFile1.png")
        self.create_file(file1)
        file2 = os.path.join(folder_dir, "testFile2.png")
        self.create_file(file2)
        file3 = os.path.join(folder_dir, "testFile3.png")
        self.create_file(file3)

        file_list = OsUtility.get_file_list(folder_dir)
        shutil.rmtree(folder_dir)

        self.assertEqual(3, len(file_list))
        self.assertTrue(file1 in file_list)
        self.assertTrue(file2 in file_list)
        self.assertTrue(file3 in file_list)

    def test_get_file_list_invalid_path(self):
        self.assertRaises(
            FileNotFoundError,
            OsUtility.get_file_list, os.path.join("", "TestData", "moreFilesFolder")
        )

    def test_get_file_list_from_not_existing_folder(self):
        self.assertRaises(
            FileNotFoundError,
            OsUtility.get_file_list, os.path.join("", "TestData", "notExistingFolder")
        )

    def test_get_file_list_with_empty_string_as_folder(self):
        self.assertRaises(
            FileNotFoundError,
            OsUtility.get_file_list, ""
        )

    def test_get_file_list_with_relative_folder_path(self):
        folder_dir = os.path.join("", "TestData", "singleFileFolder")
        self.create_folder(folder_dir)

        file = os.path.join(folder_dir, "testFile.png")
        self.create_file(file)

        file_list = OsUtility.get_file_list(folder_dir)
        shutil.rmtree(folder_dir)

        self.assertEqual(1, len(file_list))

    def test_get_file_list_with_absolute_folder_path(self):
        folder_dir = os.path.abspath(os.path.join("", "TestData", "singleFileFolder"))
        self.create_folder(folder_dir)

        file = os.path.join(folder_dir, "testFile.png")
        self.create_file(file)

        file_list = OsUtility.get_file_list(folder_dir)
        shutil.rmtree(folder_dir)

        self.assertEqual(1, len(file_list))

    def test_get_file_list_with_file_as_folder_path(self):
        self.assertRaises(
            ValueError,
            OsUtility.get_file_list, os.path.join("", "TestData", "singlePagePdf.pdf")
        )

    def test_get_file_list_with_empty_ending(self):
        folder_dir = os.path.join("", "TestData", "moreFilesFolder")
        self.create_folder(folder_dir)

        file1 = os.path.join(folder_dir, "testFile1.png")
        self.create_file(file1)
        file2 = os.path.join(folder_dir, "testFile2.pdf")
        self.create_file(file2)
        file3 = os.path.join(folder_dir, "testFile3.svg")
        self.create_file(file3)

        file_list = OsUtility.get_file_list(folder_dir, "")
        shutil.rmtree(folder_dir)

        self.assertEqual(3, len(file_list))
        self.assertTrue(file1 in file_list)
        self.assertTrue(file2 in file_list)
        self.assertTrue(file3 in file_list)

    def test_get_file_list_with_custom_ending(self):
        folder_dir = os.path.abspath(os.path.join("", "TestData", "moreFilesFolder"))
        self.create_folder(folder_dir)

        file1 = os.path.join(folder_dir, "testFile1.png")
        self.create_file(file1)
        file2 = os.path.join(folder_dir, "testFile2.pdf")
        self.create_file(file2)
        file3 = os.path.join(folder_dir, "testFile3.svg")
        self.create_file(file3)

        file_list = OsUtility.get_file_list(folder_dir, ".svg")
        shutil.rmtree(folder_dir)

        self.assertEqual(1, len(file_list))
        self.assertTrue(file3 in file_list)

    def test_get_file_list_with_dot_as_ending(self):
        folder_dir = os.path.join("", "TestData", "moreFilesFolder")
        self.create_folder(folder_dir)

        file1 = os.path.join(folder_dir, "testFile1.png")
        self.create_file(file1)
        file2 = os.path.join(folder_dir, "testFile2.pdf")
        self.create_file(file2)

        file_list = OsUtility.get_file_list(folder_dir, ".")

        self.assertEqual(0, len(file_list))

        file3 = os.path.join(folder_dir, "testFile3.")
        self.create_file(file3)

        file_list = OsUtility.get_file_list(folder_dir, ".")

        if os.name == "nt":
            self.fail("Not Supported for windows")

        self.assertEqual(1, len(file_list))
        shutil.rmtree(folder_dir)

    def test_get_file_with_text_as_ending(self):
        folder_dir = os.path.join("", "TestData", "moreFilesFolder")
        self.create_folder(folder_dir)

        file1 = os.path.join(folder_dir, "testFile1.png")
        self.create_file(file1)
        file2 = os.path.join(folder_dir, "testFile2.pdf")
        self.create_file(file2)

        file_list = OsUtility.get_file_list(folder_dir, "endswithText")

        self.assertEqual(0, len(file_list))

        file3 = os.path.join(folder_dir, "testFile3endswithText")
        self.create_file(file3)

        file_list = OsUtility.get_file_list(folder_dir, "endswithText")

        self.assertEqual(1, len(file_list))
        shutil.rmtree(folder_dir)

    # clean_up_folder
    def test_clean_up_folder_with_empty_folder(self):
        folder_dir = os.path.join("", "TestData", "emptyFolder")
        self.create_folder(folder_dir)

        OsUtility.clean_up_folder(folder_dir)

        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_files_in_folder(self):
        folder_dir = os.path.join("", "TestData", "filledFolder")
        self.create_folder(folder_dir)

        self.create_file(os.path.join(folder_dir, "testFile1.png"))
        self.create_file(os.path.join(folder_dir, "testFile2.png"))

        OsUtility.clean_up_folder(folder_dir)

        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_not_existing_folder(self):
        self.assertRaises(
            FileNotFoundError,
            OsUtility.clean_up_folder, "./TestData/notAFolder"
        )

    def test_clean_up_folder_with_relative_path_to_existing_file(self):
        file = os.path.join("", "TestData", "fileToDelete.png")
        self.create_file(file)
        self.assertRaises(
            ValueError,
            OsUtility.clean_up_folder, file
        )
        os.remove(file)

    def test_clean_up_folder_with_absolute_path_to_existing_file(self):
        file = os.path.join("", "TestData", "fileToDelete.png")
        self.create_file(file)
        self.assertRaises(
            ValueError,
            OsUtility.clean_up_folder, os.path.abspath(file)
        )
        os.remove(file)

    def test_clean_up_folder_with_relative_path_to_existing_folder(self):
        folder_dir = os.path.abspath(os.path.join("", "TestData", "existingFolder"))
        self.create_folder(folder_dir)

        OsUtility.clean_up_folder(folder_dir)
        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_absolute_path_to_existing_folder(self):
        folder_dir = os.path.join("", "TestData", "existingFolder")
        self.create_folder(folder_dir)

        OsUtility.clean_up_folder(folder_dir)
        self.assertFalse(os.path.exists(folder_dir))

    def test_clean_up_folder_with_empty_path_string(self):
        self.assertRaises(
            FileNotFoundError,
            OsUtility.clean_up_folder, ""
        )

    # get_filename
    def test_get_filename_with_file_without_file_ending(self):
        file = os.path.join("./TestData/fileWithoutFileEnding")
        self.assertEqual("fileWithoutFileEnding", OsUtility.get_filename(file))

    def test_get_filename_with_relative_path_to_file(self):
        file = os.path.join("./singlePagePdf.pdf")
        self.assertEqual("singlePagePdf", OsUtility.get_filename(file))

    def test_get_filename_with_absolute_path_to_file(self):
        file = os.path.join(os.path.abspath("TestData/singlePagePdf.pdf"))
        self.assertEqual("singlePagePdf", OsUtility.get_filename(file))

    def test_get_filename_with_relative_path_to_folder(self):
        file = os.path.join("TestData/TestFolder")
        self.assertEqual("TestFolder", OsUtility.get_filename(file))

    def test_get_filename_with_absolute_path_to_folder(self):
        file = os.path.join(os.path.abspath(os.path.join("", "TestData", "TestFolder")))
        self.assertEqual("TestFolder", OsUtility.get_filename(file))

    def test_get_filename_with_invalid_path(self):
        file = os.path.join(os.path.abspath("TestData/singlePagePdf.pdf"))
        self.assertEqual("singlePagePdf", OsUtility.get_filename(file))

        file2 = os.path.join(os.path.abspath("SomeRubishTest-LALA-File_folder(jjkn)"))
        self.assertEqual("SomeRubishTest-LALA-File_folder(jjkn)", OsUtility.get_filename(file2))

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
            OsUtility.get_config,
            self.CONFIG_FILE
        )
        # move tmp file back
        shutil.move(self.CONFIG_FILE + ".tmp", self.CONFIG_FILE)

    def test_os_utility_get_config_all_values_set(self):
        # no error -> all must have been set
        OsUtility.get_config(self.CONFIG_FILE)

    def test_os_utility_get_config_not_all_values_are_set(self):
        shutil.copyfile(self.CONFIG_FILE, self.CONFIG_FILE + ".tmp")

        with open(self.CONFIG_FILE, "r") as config_file:
            json = jsons.loads(config_file.read())

        with open(self.CONFIG_FILE, "w") as config_file:
            json.pop("cpdfsqueeze_path", None)
            config_file.write(jsons.dumps(json))
        self.assertRaises(
            TypeError,
            OsUtility.get_config,
            self.CONFIG_FILE
        )
        shutil.move(self.CONFIG_FILE + ".tmp", self.CONFIG_FILE)

    def test_os_utility_get_file_size_file_doesnt_exist(self):
        self.assertEqual(0, OsUtility.get_file_size(os.path.join("", "file_not_exists.pdf")))

    def test_os_utility_get_file_size_relative_path(self):
        self.assertNotEqual(0, OsUtility.get_file_size(os.path.join("", "TestData", "singlePagePdf.pdf")))

    def test_os_utility_get_file_size_absolute_path(self):
        self.assertNotEqual(0, OsUtility.get_file_size(
            os.path.abspath(os.path.join("", "TestData", "singlePagePdf.pdf")))
        )

    def test_os_utility_get_file_size_compare_results(self):
        self.assertTrue(
            OsUtility.get_file_size(os.path.join("", "TestData", "singlePagePdf.pdf"))
            <
            OsUtility.get_file_size(os.path.join("", "TestData", "multiPageTestData.pdf"))
        )

    def test_os_utility_get_file_size_on_filled_folder(self):
        self.assertEqual(0, OsUtility.get_file_size(os.path.join("", "TestData")))

    def test_os_utility_get_file_size_on_empty_folder(self):
        empty_dir = os.path.join("", "TestData", "emptyFolder")
        if not os.path.isdir(empty_dir):
            os.mkdir(empty_dir)
        self.assertEqual(0, OsUtility.get_file_size(empty_dir))
        os.removedirs(empty_dir)

    def test_os_utility_get_file_size_on_not_existing_folder(self):
        empty_dir = os.path.join("", "TestData", "not_existing_folder")
        if os.path.isdir(empty_dir):
            os.removedirs(empty_dir)
        self.assertEqual(0, OsUtility.get_file_size(empty_dir))

    def test_get_path_without_file_ending(self):
        file_without = os.path.join(".", "directory", "file")
        file_with = file_without + ".txt"
        self.assertEqual(file_without, OsUtility.get_path_without_file_ending(file_with))

    @classmethod
    def tearDownClass(cls) -> None:
        # reset if get_config() test has failed
        if os.path.exists(cls.CONFIG_FILE + ".tmp"):
            shutil.move(cls.CONFIG_FILE + ".tmp", cls.CONFIG_FILE)
