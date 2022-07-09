from Project.Utility.ConsoleUtility import ConsoleUtility


class CompressException(Exception):
    def __init__(self, stage="Compression"):
        super().__init__(ConsoleUtility.get_error_string("[!] Compression Failed during " + stage + " stage."))
