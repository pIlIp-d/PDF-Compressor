from unittest import TestCase

from django_app.utility.console_utility import ConsoleUtility
from tests.help_classes import get_console_buffer


class ConsoleUtilityTest(TestCase):
    
    def test_print_quiet_mode_is_not_active(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print("test")
        self.assertEqual("test\n", console_buffer.getvalue())

    def test_print_quiet_mode_is_active(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = True
        ConsoleUtility.print("test")

        # reset to default
        ConsoleUtility.quiet_mode = False

        self.assertEqual("", console_buffer.getvalue())

    def test_print_with_empty_string(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print("")
        self.assertEqual("\n", console_buffer.getvalue())

    def test_get_error_string_with_valid_string(self):
        console_buffer = get_console_buffer("stderr")
        ConsoleUtility.print_error("test_error")
        self.assertEqual("test_error\n", console_buffer.getvalue())

    def test_print_error_string_with_quiet_mode_active(self):
        console_buffer = get_console_buffer("stderr")
        ConsoleUtility.quiet_mode = True
        ConsoleUtility.print_error("test_error")
        self.assertEqual("", console_buffer.getvalue())

    def test_print_stats_with_zero_as_orig(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(0, 150)
        self.assertTrue(console_buffer.getvalue().__contains__("0%"))

    def test_print_stats_with_negative_orig(self):
        ConsoleUtility.quiet_mode = False
        self.assertRaises(
            ValueError,
            ConsoleUtility.print_stats, -5, 150
        )

    def test_print_stats_orig_smaller_than_result(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(100, 150)
        self.assertTrue(console_buffer.getvalue().__contains__("50.0%"))

    def test_print_stats_orig_bigger_than_result(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(200, 150)
        self.assertTrue(console_buffer.getvalue().__contains__("-25.0%"))

    def test_print_stats_orig_equal_to_result(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(150, 150)
        self.assertTrue(console_buffer.getvalue().__contains__("-0.0%"))

    def test_print_stats_with_zero_as_result(self):
        console_buffer = get_console_buffer("stdout")
        ConsoleUtility.quiet_mode = False
        ConsoleUtility.print_stats(150, 0)
        self.assertTrue(console_buffer.getvalue().__contains__("-100.0%"))

    def test_print_stats_with_negative_result(self):
        ConsoleUtility.quiet_mode = False
        self.assertRaises(
            ValueError,
            ConsoleUtility.print_stats, 150, -5
        )
