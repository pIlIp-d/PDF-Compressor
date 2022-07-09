RED = "\033[0;31m"
END = "\033[0m"


class ConvertException(Exception):
    def __init__(self, stage="Converting"):
        super().__init__(RED + "[!] Converting Failed during " + stage + " stage." + END)

