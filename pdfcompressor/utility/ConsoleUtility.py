class ConsoleUtility:
    RED: str = "\033[0;31m"
    YELLOW: str = "\033[0;33;33m"
    GREEN: str = "\n\033[0;32m"
    END: str = "\033[0m"

    QUIET_MODE: bool = False

    @staticmethod
    def get_error_string(string: str) -> str:
        # returns string but in red for ANSI compatible shells
        return ConsoleUtility.RED + string + ConsoleUtility.END

    @staticmethod
    def get_file_string(file: str) -> str:
        # returns string but in yellow for ANSI compatible shells
        return ConsoleUtility.YELLOW + str(file) + ConsoleUtility.END

    @staticmethod
    def print_stats(orig: int, result: int) -> None:
        ConsoleUtility.print(ConsoleUtility.GREEN + "Compressed File from " + str(round(orig / 1000000, 2)) + "mb to " +str(
            round(result / 1000000, 2)) + "mb (-" + str(
            round(100 - (result / orig * 100), 2)) + "%)" + ConsoleUtility.END)

    @staticmethod
    def print(string: str) -> None:
        if not ConsoleUtility.QUIET_MODE:
            print(string)
