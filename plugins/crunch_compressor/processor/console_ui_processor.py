from ..processor.postprocessor import Postprocessor
from ..processor.preprocessor import Preprocessor
from ..utility.console_utility import ConsoleUtility
from ..utility.os_utility import OsUtility


class ConsoleUIProcessor(Preprocessor, Postprocessor):

    def preprocess(self, source_file: str, destination_file: str) -> None:
        ConsoleUtility.print("Compressing " + ConsoleUtility.get_file_string(source_file))

    def postprocess(self, source_file: str, destination_file: str) -> None:
        ConsoleUtility.print_stats(
            OsUtility.get_file_size(source_file), OsUtility.get_file_size(destination_file), "File"
        )
        ConsoleUtility.print("")
