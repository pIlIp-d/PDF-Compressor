class ConsoleUtility:
    RED: str = "\033[0;31m"
    YELLOW: str = "\033[0;33;33m"
    GREEN: str = "\n\033[0;32m"
    END: str = "\033[0m"

    quiet_mode: bool = False

    @staticmethod
    def get_error_string(string: str) -> str:
        # returns string but in red for ANSI compatible shells
        return ConsoleUtility.RED + string + ConsoleUtility.END

    @staticmethod
    def get_file_string(file: str) -> str:
        # returns string but in yellow for ANSI compatible shells
        return ConsoleUtility.YELLOW + str(file) + ConsoleUtility.END

    @staticmethod
    def print_stats(orig: int, result: int, is_file: bool = True) -> None:
        if orig <= 0:
            raise ValueError("orig must be greater than 0")
        if result < 0:
            raise ValueError("result can't be less than 0")

        prefix = "Compressed File from " if is_file else "Compressed All from "
        ConsoleUtility.print(ConsoleUtility.GREEN + prefix + str(round(orig / 1000000, 2)) + "mb to " +str(
            round(result / 1000000, 2)) + "mb (-" + str(
            round(100 - (result / orig * 100), 2)) + "%)" + ConsoleUtility.END)

    @staticmethod
    def print_error(string: str) -> None:
        if not ConsoleUtility.quiet_mode:
            print(ConsoleUtility.get_error_string(string))

    @staticmethod
    def print(string: str) -> None:
        if not ConsoleUtility.quiet_mode:
            print(string)
