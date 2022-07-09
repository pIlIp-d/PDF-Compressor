RED = "\033[0;31m"
END = "\033[0m"


class CompressException(Exception):
    def __init__(self, stage="Compression"):
        super().__init__(RED + "[!] Compression Failed during " + stage + " stage." + END)
