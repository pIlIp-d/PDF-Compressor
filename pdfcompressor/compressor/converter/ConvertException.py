from pdfcompressor.utility.ConsoleUtility import ConsoleUtility


class ConvertException(Exception):
    def __init__(self, stage: str = "Converting"):
        super().__init__(ConsoleUtility.get_error_string(f"[!] Converting Error during {stage} stage."))

