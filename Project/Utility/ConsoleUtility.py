class ConsoleUtility:
    RED = "\033[0;31m"
    YELLOW = "\033[0;33;33m"
    GREEN = "\n\033[0;32m"
    END = "\033[0m"

    def get_error_string(self, string) -> str:
        # returns string but in red for ANSI compatible shells
        return self.RED + string + self.END

    def get_file_string(self, file) -> str:
        # returns string but in yellow for ANSI compatible shells
        return self.YELLOW + str(file) + self.END
