from ..processor.postprocessor import Postprocessor
from ..processor.preprocessor import Preprocessor
from ..utility.console_utility import ConsoleUtility
from ..utility.os_utility import OsUtility


class ConsoleUIProcessor(Preprocessor, Postprocessor):

    def preprocess(self, source: str, destination: str) -> None:
        ConsoleUtility.print("Compressing " + ConsoleUtility.get_file_string(source))

    def postprocess(self, source: str, destination: str) -> None:
        ConsoleUtility.print_stats(OsUtility.get_file_size(source), OsUtility.get_file_size(destination), "File")
        ConsoleUtility.print("")
