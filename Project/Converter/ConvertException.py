from Project.Utility.ConsoleUtility import ConsoleUtility


class ConvertException(Exception):
    def __init__(self, stage="Converting"):
        super().__init__(ConsoleUtility.get_error_string("[!] Converting Failed during " + stage + " stage."))

