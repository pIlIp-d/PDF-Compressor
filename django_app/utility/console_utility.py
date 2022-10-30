import sys


class ConsoleUtility:
    RED: str = "\033[0;31m"
    YELLOW: str = "\033[0;33;33m"
    GREEN: str = "\033[0;32m"
    END: str = "\033[0m"

    quiet_mode: bool = False
    show_errors_always: bool = False

    @classmethod
    def get_error_string(cls, string: str) -> str:
        # returns string but in red for ANSI compatible shells
        return cls.RED + string + cls.END

    @classmethod
    def get_file_string(cls, file: str) -> str:
        # returns string but in yellow for ANSI compatible shells
        return cls.YELLOW + str(file) + cls.END

    @classmethod
    def print_stats(cls, orig: int, result: int) -> None:
        if not cls.quiet_mode:
            if orig < 0:
                raise ValueError("orig must be greater than or equal to 0")
            if result < 0:
                raise ValueError("result can't be less than 0")
            orig_size = str(round(orig / 1000000, 2))
            result_size = str(round(result / 1000000, 2))
            percentage = 0 if orig == 0 else str(-1 * round(100 - (result / orig * 100), 2))
            cls.print_green(f"Compressed Files. Size: from {orig_size}mb to {result_size}mb ({percentage}%)\n")

    @classmethod
    def print_error(cls, string: str) -> None:
        if not cls.quiet_mode:
            print(string, file=sys.stderr)

    @classmethod
    def print_ansi_colored_string(cls, ansi_color_string: str, string: str, force_print: bool = False) -> None:
        if not cls.quiet_mode or force_print:
            cls.print(ansi_color_string + string + cls.END)

    @classmethod
    def print_green(cls, string: str) -> None:
        cls.print_ansi_colored_string(cls.GREEN, string)

    @classmethod
    def print(cls, string: str) -> None:
        if not cls.quiet_mode:
            print(string)
