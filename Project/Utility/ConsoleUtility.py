class ConsoleUtility:
    RED = "\033[0;31m"
    YELLOW = "\033[0;33;33m"
    GREEN = "\n\033[0;32m"
    END = "\033[0m"

    @staticmethod
    def get_error_string(string: str) -> str:
        # returns string but in red for ANSI compatible shells
        return ConsoleUtility.RED + string + ConsoleUtility.END

    @staticmethod
    def get_file_string(file: str) -> str:
        # returns string but in yellow for ANSI compatible shells
        return ConsoleUtility.YELLOW + str(file) + ConsoleUtility.END
