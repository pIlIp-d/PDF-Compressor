from ..utility.console_utility import ConsoleUtility


class CompressException(Exception):
    def __init__(self, stage: str = "Compression"):
        super().__init__(ConsoleUtility.get_error_string("[!] Compression Failed during " + stage + " stage."))
