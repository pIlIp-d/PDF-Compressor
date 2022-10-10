import sys
from io import StringIO
from unittest import TestCase

from plugins.pdfcompressor.utility.console_utility import ConsoleUtility

# TODO update testTables


class ConsoleUtilityTest(TestCase):
    @staticmethod
    def get_console_buffer(std_type: str) -> StringIO:
        console_buffer = StringIO()
        if std_type == "stdout":
            sys.stdout = console_buffer
        elif std_type == "stderr":
            sys.stderr = console_buffer
        else:
            raise ValueError("unsupported std_type")
        return console_buffer

    def test_print_quiet_mode_is_not_active(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print("test")
        self.assertEqual("test\n", console_buffer.getvalue())

    def test_print_quiet_mode_is_active(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = True
        ConsoleUtility.print("test")

        # reset to default
        ConsoleUtility.quiet_mode = False

        self.assertEqual("", console_buffer.getvalue())

    def test_print_with_empty_string(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print("")
        self.assertEqual("\n", console_buffer.getvalue())

    def test_get_error_string_with_valid_string(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stderr")
        ConsoleUtility.print_error("test_error")
        self.assertEqual("test_error\n", console_buffer.getvalue())

    def test_print_error_string_with_quiet_mode_active(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stderr")
        ConsoleUtility.quiet_mode = True
        ConsoleUtility.print_error("test_error")
        self.assertEqual("", console_buffer.getvalue())

    def test_print_stats_with_zero_as_orig(self):
        ConsoleUtility.quiet_mode = False
        self.assertRaises(
            ValueError,
            ConsoleUtility.print_stats, 0, 150, "File"
        )

    def test_print_stats_with_negative_orig(self):
        ConsoleUtility.quiet_mode = False
        self.assertRaises(
            ValueError,
            ConsoleUtility.print_stats, -5, 150, "File"
        )

    def test_print_stats_orig_smaller_than_result(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(100, 150, "File")
        self.assertTrue(console_buffer.getvalue().__contains__("-50.0%"))

    def test_print_stats_orig_bigger_than_result(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(200, 150, "File")
        self.assertTrue(console_buffer.getvalue().__contains__("-25.0%"))

    def test_print_stats_orig_equal_to_result(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(150, 150, "File")
        self.assertTrue(console_buffer.getvalue().__contains__("-0.0%"))

    def test_print_stats_with_zero_as_result(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(150, 0, "File")
        self.assertTrue(console_buffer.getvalue().__contains__("-100.0%"))

    def test_print_stats_with_empty_string_as_compressed_value(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(150, 0, "")
        self.assertTrue(console_buffer.getvalue().__contains__("  "))

    def test_print_stats_normal_compressed_value(self):
        console_buffer = ConsoleUtilityTest.get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(150, 0, "File")
        self.assertTrue(console_buffer.getvalue().__contains__("File"))

    def test_print_stats_with_negative_result(self):
        ConsoleUtility.quiet_mode = False
        self.assertRaises(
            ValueError,
            ConsoleUtility.print_stats, 150, -5, "File"
        )
