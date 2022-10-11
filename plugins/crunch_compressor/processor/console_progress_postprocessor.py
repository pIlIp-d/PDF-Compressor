from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from plugins.crunch_compressor.utility.console_utility import ConsoleUtility


class ConsoleProgressPostprocessor(Postprocessor):
    def __init__(self, max_amount: int, pre_message: str = "", post_message: str = ""):
        if max_amount <= 0:
            raise ValueError(f"'max' must be positive but was '{max}'")
        self.__max_amount = max_amount
        self.__progress = 0
        self.__pre_message = pre_message
        self.__post_message = post_message

    def postprocess(self, source: str, destination: str) -> None:
        self.__progress += 1
        ConsoleUtility.print(f"** - {self.__pre_message} {self.__progress}/{self.__max_amount} {self.__post_message}")
