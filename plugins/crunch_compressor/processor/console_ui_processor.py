from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from django_app.plugin_system.processing_classes.preprocessor import Preprocessor
from django_app.utility.os_utility import OsUtility
from django_app.utility.console_utility import ConsoleUtility


class ConsoleUIProcessor(Preprocessor, Postprocessor):

    def preprocess(self, source_file: str, destination_file: str) -> None:
        ConsoleUtility.print("Compressing " + ConsoleUtility.get_file_string(source_file))

    def postprocess(self, source_file: str, destination_file: str) -> None:
        ConsoleUtility.print_stats(
            OsUtility.get_file_size(source_file), OsUtility.get_file_size(destination_file), "File"
        )
        ConsoleUtility.print("")
