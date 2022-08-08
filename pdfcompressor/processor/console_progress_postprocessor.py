from pdfcompressor.processor.postprocessor import Postprocessor
from pdfcompressor.utility.console_utility import ConsoleUtility


class ConsoleProgressPostprocessor(Postprocessor):
    def __init__(self, max: int, pre_message: str = "", post_message: str = ""):
        if max <= 0:
            raise ValueError(f"'max' must be positive but was '{max}'")
        self.__max = max
        self.__progress = 0
        self.__pre_message = pre_message
        self.__post_message = post_message

    def postprocess(self, source: str, destination: str) -> None:
        ConsoleUtility.print(f"** - {self.__pre_message} {self.__progress + 1}/{self.__max} {self.__post_message}")
