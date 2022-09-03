class ConsoleUtility:
    RED: str = "\033[0;31m"
    YELLOW: str = "\033[0;33;33m"
    GREEN: str = "\033[0;32m"
    END: str = "\033[0m"

    quiet_mode: bool = False

    @classmethod
    def get_error_string(cls, string: str) -> str:
        # returns string but in red for ANSI compatible shells
        return cls.RED + string + cls.END

    @classmethod
    def get_file_string(cls, file: str) -> str:
        # returns string but in yellow for ANSI compatible shells
        return cls.YELLOW + str(file) + cls.END

    @classmethod
    def print_stats(cls, orig: int, result: int, compressed_value: str) -> None:
        if not cls.quiet_mode:
            if orig <= 0:
                raise ValueError("orig must be greater than 0")
            if result < 0:
                raise ValueError("result can't be less than 0")

            cls.print(cls.GREEN + f"Compressed {compressed_value} from " + str(round(orig / 1000000, 2)) + "mb to " + str(
                round(result / 1000000, 2)) + "mb (-" + str(
                round(100 - (result / orig * 100), 2)) + "%)" + cls.END)

    @classmethod
    def print_error(cls, string: str) -> None:
        cls.print(cls.get_error_string(string))

    @classmethod
    def print_ansi_colored_string(cls, color: str, string: str) -> None:
        cls.print(color + string + cls.END)

    @classmethod
    def print_green(cls, string: str) -> None:
        cls.print_ansi_colored_string(cls.GREEN, string)

    @classmethod
    def print(cls, string: str) -> None:
        if not cls.quiet_mode:
            print(string)
